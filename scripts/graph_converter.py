"""
Handles the conversion of Pydantic models to a NetworkX graph structure.

This enhanced version includes:
- A two-pass system to handle both direct object relationships and indirect, name-based relationships.
- Content-based entity resolution for deduplication.
"""
from pydantic import BaseModel
import networkx as nx
import hashlib
from typing import Any, Dict, List, Tuple

class GraphConverter:
    """
    Converts Pydantic models into a NetworkX graph, handling both direct and name-based relationships.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        # This map stores (name, label) -> node_id, e.g., (("Dégâts des eaux", "Guarantee"), "Guarantee_7947...")
        self.name_to_id_map: Dict[Tuple[str, str], str] = {}
        self._visited_ids = set()


    def _get_node_id(self, model_instance: BaseModel) -> str:
        """Creates a deterministic, content-based ID for a node."""
        node_label = model_instance.__class__.__name__
        
        # Define key fields for creating a unique signature for each entity type
        # We use 'name' as the primary key for these models.
        id_fields = {
            "InsurancePlan": ["name"],
            "Guarantee": ["name"],
            "HomeInsurance": ["product_name"],
            # Add other types as needed
            "Person": ["name"],
            "Organization": ["name"],
            "Address": ["street", "city", "postal_code"],
            "Invoice": ["bill_no"],
        }.get(node_label, [])

        if not id_fields:
            # Fallback for models without a 'name' or key field (like ReimbursementCondition)
            model_string = str(model_instance.model_dump())
        else:
            # Create a stable string from the key fields
            model_string = "|".join(
                str(getattr(model_instance, f, "")).lower() for f in id_fields
            )
            
        hash_id = hashlib.sha256(model_string.encode()).hexdigest()
        return f"{node_label}_{hash_id[:12]}"

    def _create_nodes_and_map(self, model_instance: BaseModel):
        """Pass 1: Recursively create all nodes and populate the name-to-ID map."""
        if not isinstance(model_instance, BaseModel):
            return

        node_id = self._get_node_id(model_instance)
        
        if node_id not in self.graph:
            node_label = model_instance.__class__.__name__
            
            # Separate properties from fields that define relationships
            node_properties = {}
            for k, v in model_instance.model_dump().items():
                is_edge_field = (
                    model_instance.model_fields[k].json_schema_extra and 
                    'edge_label' in model_instance.model_fields[k].json_schema_extra
                )
                if not is_edge_field:
                    node_properties[k] = v

            self.graph.add_node(node_id, label=node_label, **node_properties)

            # If the node has a 'name', add it to our lookup map
            if hasattr(model_instance, 'name'):
                self.name_to_id_map[(model_instance.name, node_label)] = node_id

        # Recurse through children
        for field_name in model_instance.model_fields:
            child_objects = getattr(model_instance, field_name)
            if not isinstance(child_objects, list):
                child_objects = [child_objects]
            
            for item in child_objects:
                if isinstance(item, BaseModel):
                    self._create_nodes_and_map(item)

    def _create_edges(self, model_instance: BaseModel):
        """Pass 2: Recursively create all edges, including name-based ones."""
        if not isinstance(model_instance, BaseModel) or model_instance.__class__.__name__ == "Guarantee":
            # Avoid recursing into Guarantee to prevent circular dependencies if any
            # and stop if this instance has already been processed for edges.
            return

        current_node_id = self._get_node_id(model_instance)
        
        # Check if we've already processed edges for this node
        if current_node_id in self._visited_ids:
            return
        self._visited_ids.add(current_node_id)


        for field_name, field_info in model_instance.model_fields.items():
            if field_info.json_schema_extra and 'edge_label' in field_info.json_schema_extra:
                edge_label = field_info.json_schema_extra['edge_label']
                child_objects = getattr(model_instance, field_name)

                if child_objects is None:
                    continue

                if not isinstance(child_objects, list):
                    child_objects = [child_objects]

                for item in child_objects:
                    if isinstance(item, BaseModel):
                        # --- Handle direct object links ---
                        child_node_id = self._get_node_id(item)
                        if self.graph.has_node(child_node_id):
                            self.graph.add_edge(current_node_id, child_node_id, label=edge_label)
                        # Recurse to create edges from the child
                        self._create_edges(item)
                    
                    elif isinstance(item, str) and 'target_label' in field_info.json_schema_extra:
                        # --- Handle name-based links ---
                        target_label = field_info.json_schema_extra['target_label']
                        if (item, target_label) in self.name_to_id_map:
                            target_node_id = self.name_to_id_map[(item, target_label)]
                            self.graph.add_edge(current_node_id, target_node_id, label=edge_label)
        
    def pydantic_to_graph(self, root_model: BaseModel) -> nx.DiGraph:
        """
        Converts the Pydantic model to a NetworkX graph using a two-pass system.
        """
        # Clear previous state
        self.graph.clear()
        self.name_to_id_map.clear()
        self._visited_ids.clear()

        # Pass 1: Create all nodes and the name-to-ID map
        self._create_nodes_and_map(root_model)
        # Pass 2: Create all edges using the populated graph and map
        self._create_edges(root_model)
        
        return self.graph

    def to_json_serializable(self) -> dict:
        """
        Exports the graph to a backend-agnostic, JSON-friendly format.
        """
        graph_data = nx.node_link_data(self.graph)
        
        # Reformat for clarity and common graph DB import formats
        nodes = [{"id": n["id"], "type": n.get("label", ""), "properties": {k:v for k,v in n.items() if k not in ["id", "label"]}} for n in graph_data["nodes"]]
        edges = [{"source": e["source"], "target": e["target"], "label": e.get("label", "")} for e in graph_data["links"]]
        
        return {"nodes": nodes, "edges": edges}
