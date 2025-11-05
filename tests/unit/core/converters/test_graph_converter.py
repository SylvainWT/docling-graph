from typing import List, Optional

import pytest
from pydantic import BaseModel, Field

from docling_graph.core.converters.config import GraphConfig
from docling_graph.core.converters.graph_converter import GraphConverter


# --- Test Pydantic Models ---

class SimpleModel(BaseModel):
    name: str = Field(..., graph_key=True)
    age: int


class Company(BaseModel):
    name: str = Field(..., graph_key=True)
    location: str


class Person(BaseModel):
    name: str = Field(..., graph_key=True)
    works_for: Optional[Company] = None
    friends: List["Person"] = []


# Rebuild forward refs
Person.model_rebuild()

# --- Tests ---

@pytest.fixture
def default_config():
    return GraphConfig()


@pytest.fixture
def converter(default_config):
    return GraphConverter(config=default_config)


def test_converter_init(converter):
    """Test converter initialization."""
    assert converter.registry is not None
    assert converter.edges == []
    assert converter.config.use_raw_edge_labels is False


def test_convert_simple_model(converter):
    """Test converting a single, simple model."""
    model = SimpleModel(name="Alice", age=30)
    converter.convert(model)
    graph = converter.get_graph()

    assert len(graph["nodes"]) == 1
    assert len(graph["edges"]) == 0
    assert graph["nodes"][0]["id"] == "simplemodel-1"
    assert graph["nodes"][0]["label"] == "SimpleModel"
    assert graph["nodes"][0]["properties"]["name"] == "Alice"
    assert graph["nodes"][0]["properties"]["age"] == 30


def test_convert_nested_model_creates_edge(converter):
    """Test that a nested model creates two nodes and one edge."""
    company = Company(name="Acme Inc.", location="NY")
    person = Person(name="Alice", works_for=company)

    converter.convert(person)
    graph = converter.get_graph()

    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1

    # Check for Person node
    person_node = next(n for n in graph["nodes"] if n["label"] == "Person")
    assert person_node["properties"]["name"] == "Alice"
    assert person_node["id"] == "person-1"

    # Check for Company node
    company_node = next(n for n in graph["nodes"] if n["label"] == "Company")
    assert company_node["properties"]["name"] == "Acme Inc."
    assert company_node["id"] == "company-1"

    # Check for edge
    edge = graph["edges"][0]
    assert edge["source"] == person_node["id"]
    assert edge["target"] == company_node["id"]
    assert edge["label"] == "WORKS_FOR"  # Default is uppercase


def test_convert_list_of_models_creates_edges(converter):
    """Test a list of nested models."""
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    charlie = Person(name="Charlie", friends=[alice, bob])

    converter.convert(charlie)
    graph = converter.get_graph()

    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2

    charlie_id = next(n["id"] for n in graph["nodes"] if n["properties"]["name"] == "Charlie")
    alice_id = next(n["id"] for n in graph["nodes"] if n["properties"]["name"] == "Alice")
    bob_id = next(n["id"] for n in graph["nodes"] if n["properties"]["name"] == "Bob")

    edges = graph["edges"]
    assert {"source": charlie_id, "target": alice_id, "label": "FRIENDS"} in edges
    assert {"source": charlie_id, "target": bob_id, "label": "FRIENDS"} in edges


def test_model_deduplication(converter):
    """Test that identical nested models are not duplicated."""
    company = Company(name="Acme Inc.", location="NY")
    alice = Person(name="Alice", works_for=company)
    bob = Person(name="Bob", works_for=company)  # Works for the *same* company

    converter.convert([alice, bob])
    graph = converter.get_graph()

    # Should be 3 nodes: Alice, Bob, and *one* Acme Inc.
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2

    company_nodes = [n for n in graph["nodes"] if n["label"] == "Company"]
    assert len(company_nodes) == 1


def test_config_use_raw_edge_labels():
    """Test config to use raw field names for edge labels."""
    config = GraphConfig(use_raw_edge_labels=True)
    converter = GraphConverter(config=config)

    company = Company(name="Acme Inc.", location="NY")
    person = Person(name="Alice", works_for=company)

    converter.convert(person)
    graph = converter.get_graph()

    assert len(graph["edges"]) == 1
    edge = graph["edges"][0]
    assert edge["label"] == "works_for"  # Not "WORKS_FOR"


def test_config_use_title_case_edge_labels():
    """Test config to use title-cased field names for edge labels."""
    config = GraphConfig(use_title_case_edge_labels=True)
    converter = GraphConverter(config=config)

    company = Company(name="Acme Inc.", location="NY")
    person = Person(name="Alice", works_for=company)

    converter.convert(person)
    graph = converter.get_graph()

    assert len(graph["edges"]) == 1
    edge = graph["edges"][0]
    assert edge["label"] == "Works For"  # Not "WORKS_FOR" or "works_for"


def test_no_graph_key_field():
    """Test that a model without a `graph_key` Field raises a Warning."""

    class NoKeyModel(BaseModel):
        name: str

    model = NoKeyModel(name="Test")
    converter = GraphConverter(GraphConfig())

    # Should raise a UserWarning because no graph_key is defined
    with pytest.warns(UserWarning, match="using object hash as key"):
        converter.convert(model)
        graph = converter.get_graph()

    # It should still process the model
    assert len(graph["nodes"]) == 1
    assert graph["nodes"][0]["label"] == "NoKeyModel"