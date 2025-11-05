import pytest

from docling_graph.core.converters.node_id_registry import NodeIDRegistry


@pytest.fixture
def registry():
    """Returns a clean IdRegistry instance for each test."""
    return NodeIDRegistry()


def test_registry_init(registry):
    """Test that the registry initializes with empty structures."""
    assert registry.node_map == {}
    assert registry.label_counters == {}


def test_get_id_new_item(registry):
    """Test registering a new item."""
    properties = {"name": "Alice"}
    item_id = registry.get_id(label="Person", key="alice@example.com", properties=properties)

    assert item_id == "person-1"
    # Check that the item is stored in the node_map
    assert registry.node_map[("Person", "alice@example.com")] == ("person-1", properties)


def test_get_id_existing_item(registry):
    """Test that registering the same item key returns the same ID."""
    properties1 = {"name": "Alice"}
    item_id_1 = registry.get_id(label="Person", key="alice@example.com", properties=properties1)

    assert item_id_1 == "person-1"

    # Registering again with the same key
    properties2 = {"name": "Alice"}  # Properties can be different, key is what matters
    item_id_2 = registry.get_id(label="Person", key="alice@example.com", properties=properties2)

    # Should return the *same* ID
    assert item_id_2 == "person-1"
    assert len(registry.node_map) == 1


def test_get_id_multiple_items_same_label(registry):
    """Test multiple items with the same label get incrementing IDs."""
    item_id_1 = registry.get_id("Person", "alice", {"name": "Alice"})
    item_id_2 = registry.get_id("Person", "bob", {"name": "Bob"})

    assert item_id_1 == "person-1"
    assert item_id_2 == "person-2"
    assert registry.label_counters["Person"] == 2


def test_get_id_multiple_labels(registry):
    """Test that different labels have their own ID counters."""
    item_id_p1 = registry.get_id("Person", "alice", {"name": "Alice"})
    item_id_c1 = registry.get_id("Company", "acme", {"name": "Acme Inc."})
    item_id_p2 = registry.get_id("Person", "bob", {"name": "Bob"})
    item_id_c2 = registry.get_id("Company", "beta", {"name": "Beta Ltd."})

    assert item_id_p1 == "person-1"
    assert item_id_c1 == "company-1"
    assert item_id_p2 == "person-2"
    assert item_id_c2 == "company-2"

    assert registry.label_counters["Person"] == 2
    assert registry.label_counters["Company"] == 1  # Note: 1-indexed, so 1 means "c-1"


def test_get_all_nodes(registry):
    """Test retrieving the final list of nodes."""
    registry.get_id("Person", "alice", {"name": "Alice", "age": 30})
    registry.get_id("Company", "acme", {"name": "Acme Inc."})
    registry.get_id("Person", "alice", {"name": "Alice", "age": 30})  # Duplicate

    nodes = registry.get_all_nodes()

    assert len(nodes) == 2
    
    expected_nodes = [
        {
            "id": "person-1",
            "label": "Person",
            "properties": {"name": "Alice", "age": 30, "id": "person-1"},
        },
        {
            "id": "company-1",
            "label": "Company",
            "properties": {"name": "Acme Inc.", "id": "company-1"},
        },
    ]

    # Order isn't guaranteed, so check for presence
    assert expected_nodes[0] in nodes
    assert expected_nodes[1] in nodes


def test_label_normalization(registry):
    """Test that labels are normalized for the ID prefix."""
    item_id = registry.get_id("Complex Label", "key1", {})
    assert item_id == "complex-label-1"

    item_id_2 = registry.get_id("AnotherPerson", "key2", {})
    assert item_id_2 == "anotherperson-1"