"""
Handles the conversion of Pydantic models to a NetworkX graph structure.

This new version is fully declarative and Pydantic-driven:

1.  **Automatic Edge Discovery**: No more `json_schema_extra`. Any field that
    is a `BaseModel` or `List[BaseModel]` is automatically treated as an edge.
    The field name is used as the edge label.

2.  **Rich Edge Model**: If a field uses the `Edge[T]` model, its attributes
    (e.g., `label`, `weight`) are added directly to the graph edge.

3.  **Dynamic Node IDs**: Node uniqueness is defined *in* the Pydantic
    templates using `model_config = ConfigDict(graph_id_fields=['my_id'])`.
    This converter reads that config, removing all hardcoded logic.

4.  **Proper Attribute Handling**: Lists of primitives (e.g., `List[str]`)
    are correctly stored as lists on the node, not flattened into strings.
"""
import networkx as nx
import hashlib
import json
from pydantic import BaseModel
from typing import List, Any, Set
from .graph_models import Edge # Import the new Edge model

class GraphConverter:
    """
    Converts Pydantic models into a NetworkX graph using a declarative,
    template-driven two-pass system.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self._visited_ids: Set[str] = set()

    def _get_node_id(self, model_instance: BaseModel) -> str:
        """
        Creates a deterministic, content-based ID for a node.

        It first checks for `graph_id_fields` in the model's ConfigDict.
        If found, it builds an ID from those fields.
        If not found, it falls back to hashing the node's attributes.
        """
        node_label = model_instance.__class__.__name__
        
        # Change 2: Dynamic Node ID Generation
        # Read the 'graph_id_fields' from the model's config
        config = getattr(model_instance, 'model_config', {})
        id_fields = config.get('graph_id_fields', [])
        
        id_string = ""

        if id_fields:
            # Create a composite key from the specified fields
            id_parts = [str(getattr(model_instance, f, '')) for f in id_fields]
            id_string = ":".join(id_parts)
        
        if not id_string:
            # Fallback: Hash the node's *attributes* (not its edges)
            # This creates a stable hash based on the node's own data.
            attr_dict = {}
            for field_name in model_instance.model_fields:
                value = getattr(model_instance, field_name)
                # Check if the field is an edge (to exclude it from the hash)
                is_edge = False
                if isinstance(value, (BaseModel, Edge)):
                    is_edge = True
                elif isinstance(value, list) and value and isinstance(value[0], (BaseModel, Edge)):
                    is_edge = True

                if not is_edge:
                    # Use model_dump_json for a stable representation of the value
                    try:
                        attr_dict[field_name] = json.dumps(value, default=str, sort_keys=True)
                    except TypeError:
                        attr_dict[field_name] = str(value)
            
            # Use json.dumps for a stable, sorted representation for hashing
            id_string = json.dumps(attr_dict, sort_keys=True)

        # Generate the final ID
        hash_id = hashlib.md5(id_string.encode()).hexdigest()
        return f"{node_label}_{hash_id[:10]}"

    def _is_field_an_edge(self, value: Any) -> bool:
        """Helper to determine if a field's value represents an edge."""
        if isinstance(value, (BaseModel, Edge)):
            return True
        if isinstance(value, list) and value and isinstance(value[0], (BaseModel, Edge)):
            return True
        return False

    def _create_nodes_pass(self, model_instance: BaseModel):
        """
        Pass 1: Recursively create all nodes in the graph.
        Nodes are added, but edges are not created yet.
        """
        node_id = self._get_node_id(model_instance)
        
        if node_id in self._visited_ids:
            return  # This exact entity has been processed
        self._visited_ids.add(node_id)

        node_label = model_instance.__class__.__name__
        
        # Create node attributes
        node_attrs = {"id": node_id, "label": node_label}
        
        for field_name in model_instance.model_fields:
            value = getattr(model_instance, field_name)
            if not self._is_field_an_edge(value):
                # Change 3: Improved Attribute Handling
                # Store lists, dicts, and primitives as-is
                if isinstance(value, (str, int, float, bool, list, dict)):
                    node_attrs[field_name] = value

        self.graph.add_node(node_id, **node_attrs)

        # --- Recurse ---
        # We must still recurse to create nodes for nested models
        for field_name in model_instance.model_fields:
            value = getattr(model_instance, field_name)
            if isinstance(value, Edge):
                # If it's a rich Edge, recurse on its target
                self._create_nodes_pass(value.target)
            elif isinstance(value, BaseModel):
                # If it's a plain nested model, recurse on it
                self._create_nodes_pass(value)
            elif isinstance(value, list) and value and isinstance(value[0], (BaseModel, Edge)):
                # If it's a list of models or Edges, recurse on each item
                for item in value:
                    if isinstance(item, Edge):
                        self._create_nodes_pass(item.target)
                    elif isinstance(item, BaseModel):
                        self._create_nodes_pass(item)

    def _create_edges_pass(self, model_instance: BaseModel):
        """
        Pass 2: Recursively create all edges between existing nodes.
        This pass assumes all nodes have been created in Pass 1.
        """
        current_node_id = self._get_node_id(model_instance)

        for field_name in model_instance.model_fields:
            value = getattr(model_instance, field_name)
            
            # --- Change 1 & 4: Automatic and Rich Edge Discovery ---
            
            if isinstance(value, Edge):
                # Case 1: Rich Edge model (e.g., field: Edge[Person])
                target_node_id = self._get_node_id(value.target)
                edge_attrs = value.model_dump(exclude={'target'})
                if self.graph.has_node(target_node_id):
                    self.graph.add_edge(current_node_id, target_node_id, **edge_attrs)
                # Recurse to create edges *from* this nested model
                self._create_edges_pass(value.target)
            
            elif isinstance(value, BaseModel):
                # Case 2: Simple nested model (e.g., field: Person)
                target_node_id = self._get_node_id(value)
                if self.graph.has_node(target_node_id):
                    self.graph.add_edge(current_node_id, target_node_id, label=field_name)
                # Recurse to create edges *from* this nested model
                self._create_edges_pass(value)

            elif isinstance(value, list) and value:
                if isinstance(value[0], Edge):
                    # Case 3: List of Rich Edges (e.g., field: List[Edge[Person]])
                    for item in value:
                        target_node_id = self._get_node_id(item.target)
                        edge_attrs = item.model_dump(exclude={'target'})
                        if self.graph.has_node(target_node_id):
                            self.graph.add_edge(current_node_id, target_node_id, **edge_attrs)
                        # Recurse to create edges *from* this nested model
                        self._create_edges_pass(item.target)
                
                elif isinstance(value[0], BaseModel):
                    # Case 4: List of simple models (e.g., field: List[Person])
                    for item in value:
                        target_node_id = self._get_node_id(item)
                        if self.graph.has_node(target_node_id):
                            self.graph.add_edge(current_node_id, target_node_id, label=field_name)
                        # Recurse to create edges *from* this list item
                        self._create_edges_pass(item)

    def pydantic_list_to_graph(self, models: List[BaseModel]) -> nx.DiGraph:
        """
        Converts a LIST of Pydantic models to a single NetworkX graph.
        This is the main entry point.
        """
        # Clear previous state
        self.graph.clear()
        self._visited_ids.clear()

        # Pass 1: Create all nodes
        for root_model in models:
            self._create_nodes_pass(root_model)
        
        # Pass 2: Create all edges
        for root_model in models:
            self._create_edges_pass(root_model)
        
        return self.graph

    def to_json_serializable(self) -> dict:
        """Exports the graph to a backend-agnostic, JSON-friendly format."""
        graph_data = nx.node_link_data(self.graph)
        nodes = [{"id": n["id"], "type": n.get("label", ""), "properties": {k:v for k,v in n.items() if k not in ["id", "label"]}} for n in graph_data["nodes"]]
        edges = []
        
        for i, l in enumerate(graph_data["links"]):
            edge_data = {
                "id": f"e{i}",
                "source": l["source"],
                "target": l["target"],
                "label": l.get("label", "")
            }
            # Ensure edge properties are also serialized
            props = {k:v for k,v in l.items() if k not in ["source", "target", "label"]}
            if props:
                edge_data["properties"] = props
            edges.append(edge_data)

        return {"nodes": nodes, "edges": edges}

