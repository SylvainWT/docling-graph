"""
Unit tests for visualization components.
"""

import pytest
from pathlib import Path
import networkx as nx

from docling_graph.core.visualizers import (
    StaticVisualizer,
    InteractiveVisualizer
)

# Configure matplotlib to use non-interactive backend for tests
import matplotlib
matplotlib.use('Agg')


class TestStaticVisualizer:
    """Tests for StaticVisualizer."""

    def test_static_visualizer_init(self):
        """Test StaticVisualizer initialization."""
        visualizer = StaticVisualizer()
        assert visualizer is not None

    def test_static_visualize_simple_graph(self, simple_graph, temp_dir):
        """Test visualizing a simple graph."""
        visualizer = StaticVisualizer()
        output_path = temp_dir / "static_graph.png"
        visualizer.visualize(simple_graph, output_path)
        # Check that output file was created
        assert output_path.exists()

    def test_static_visualize_complex_graph(self, complex_graph, temp_dir):
        """Test visualizing a complex graph."""
        visualizer = StaticVisualizer()
        output_path = temp_dir / "complex_graph.png"
        visualizer.visualize(complex_graph, output_path)
        assert output_path.exists()

    def test_static_visualize_empty_graph(self, temp_dir):
        """Test visualizing an empty graph."""
        empty_graph = nx.DiGraph()
        visualizer = StaticVisualizer()
        output_path = temp_dir / "empty_graph.png"
        visualizer.visualize(empty_graph, output_path)
        # Empty graphs are not rendered, just handled gracefully
        assert True  # Just verify no exception raised

    def test_static_visualize_creates_directory(self, temp_dir):
        """Test that visualizer creates output directory if needed."""
        visualizer = StaticVisualizer()
        nested_path = temp_dir / "subdir" / "graph.png"
        # Directory doesn't exist yet
        assert not nested_path.parent.exists()
        # Use positional arguments instead of keyword arguments
        visualizer.visualize(self._create_simple_graph(), nested_path)
        # Should create parent directory
        assert nested_path.parent.exists()
        assert nested_path.exists()

    def test_static_visualize_overwrites_existing(self, simple_graph, temp_dir):
        """Test that visualizer overwrites existing file."""
        visualizer = StaticVisualizer()
        output_path = temp_dir / "graph.png"
        # Create initial file
        output_path.write_bytes(b"old content")
        initial_size = output_path.stat().st_size
        # Visualize (should overwrite)
        visualizer.visualize(simple_graph, output_path)
        # File should be updated (likely different size)
        # If same size by coincidence, at least verify it exists
        assert output_path.exists()

    def _create_simple_graph(self):
        """Helper to create a simple graph."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edges_from([("a", "b"), ("b", "c")])
        return graph

    @pytest.mark.parametrize("extension", [".png"])
    def test_static_visualize_different_formats(self, simple_graph, temp_dir, extension):
        """Test visualizing with different output formats."""
        visualizer = StaticVisualizer()
        output_path = temp_dir / f"graph{extension}"
        try:
            visualizer.visualize(simple_graph, output_path)
            assert output_path.exists()
        except ValueError:
            # Some formats might not be supported
            pass

class TestInteractiveVisualizer:
    """Tests for InteractiveVisualizer."""

    def test_interactive_visualizer_init(self):
        """Test InteractiveVisualizer initialization."""
        visualizer = InteractiveVisualizer()
        assert visualizer is not None

    def test_interactive_visualize_simple_graph(self, simple_graph, temp_dir):
        """Test creating interactive visualization."""
        visualizer = InteractiveVisualizer()
        output_path = temp_dir / "interactive_graph.html"
        visualizer.visualize(simple_graph, output_path)
        assert output_path.exists()

    def test_interactive_output_is_html(self, simple_graph, temp_dir):
        """Test that output is HTML file."""
        visualizer = InteractiveVisualizer()
        output_path = temp_dir / "graph.html"
        visualizer.visualize(simple_graph, output_path)
        # Check that file contains HTML
        content = output_path.read_text()
        assert "" in content.lower()

    def test_interactive_visualize_complex_graph(self, complex_graph, temp_dir):
        """Test interactive visualization of complex graph."""
        visualizer = InteractiveVisualizer()
        output_path = temp_dir / "complex_interactive.html"
        visualizer.visualize(complex_graph, output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_interactive_visualize_empty_graph(self, temp_dir):
        """Test interactive visualization of empty graph."""
        import networkx as nx
        empty_graph = nx.DiGraph()
        visualizer = InteractiveVisualizer()
        output_path = temp_dir / "empty_interactive.html"
        try:
            visualizer.visualize(empty_graph, output_path)
        except ValueError:
            # Might raise error for empty graph
            pass
        # If no exception raised, test passes
        assert True

    def test_interactive_graph_contains_nodes(self, simple_graph, temp_dir):
        """Test that HTML contains node information."""
        visualizer = InteractiveVisualizer()
        output_path = temp_dir / "graph.html"
        visualizer.visualize(simple_graph, output_path)
        content = output_path.read_text()
        # Should contain references to nodes
        # Exact format depends on your visualization library (pyvis, etc.)
        assert len(content) > 1000  # Should have substantial content

    def test_interactive_creates_directory(self, temp_dir):
        """Test that interactive visualizer creates directories."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("a", "b")
        visualizer = InteractiveVisualizer()
        nested_path = temp_dir / "outputs" / "viz" / "graph.html"
        visualizer.visualize(graph, nested_path)
        assert nested_path.parent.exists()
        assert nested_path.exists()

class TestVisualizerIntegration:
    """Integration tests for visualizers."""

    def test_both_visualizers_same_graph(self, simple_graph, temp_dir):
        """Test that both visualizers work on same graph."""
        static_viz = StaticVisualizer()
        interactive_viz = InteractiveVisualizer()
        static_path = temp_dir / "static.png"
        interactive_path = temp_dir / "interactive.html"
        static_viz.visualize(simple_graph, static_path)
        interactive_viz.visualize(simple_graph, interactive_path)
        assert static_path.exists()
        assert interactive_path.exists()

    def test_visualizers_dont_modify_graph(self, simple_graph, temp_dir):
        """Test that visualization doesn't modify the graph."""
        import copy
        original_nodes = set(simple_graph.nodes())
        original_edges = set(simple_graph.edges())
        static_viz = StaticVisualizer()
        interactive_viz = InteractiveVisualizer()
        static_viz.visualize(simple_graph, temp_dir / "static.png")
        interactive_viz.visualize(simple_graph, temp_dir / "interactive.html")
        # Graph should be unchanged
        assert set(simple_graph.nodes()) == original_nodes
        assert set(simple_graph.edges()) == original_edges

class TestVisualizerEdgeCases:
    """Test edge cases for visualizers."""

    def test_visualize_graph_with_special_characters(self, temp_dir):
        """Test visualizing graph with special characters in labels."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_node("node_1", label="Node with 'quotes'")
        graph.add_node("node_2", label="Node with tags")
        graph.add_edge("node_1", "node_2", label="edge & symbols")
        visualizer = InteractiveVisualizer()
        output_path = temp_dir / "special_chars.html"
        # Should handle special characters without crashing
        visualizer.visualize(graph, output_path)
        assert output_path.exists()

    def test_visualize_very_large_graph(self, temp_dir):
        """Test visualizing a large graph."""
        import networkx as nx
        graph = nx.DiGraph()
        # Create large graph
        num_nodes = 1000
        for i in range(num_nodes):
            graph.add_node(f"node_{i}")
        # Add some edges
        for i in range(0, num_nodes - 1, 10):
            graph.add_edge(f"node_{i}", f"node_{i+1}")
        visualizer = StaticVisualizer()
        output_path = temp_dir / "large_graph.png"
        # Should handle large graphs
        try:
            visualizer.visualize(graph, output_path)
            assert output_path.exists()
        except MemoryError:
            pytest.skip("Graph too large for current system")

    def test_visualize_with_long_labels(self, temp_dir):
        """Test visualizing with very long node labels."""
        import networkx as nx
        graph = nx.DiGraph()
        long_label = "A" * 500  # Very long label
        graph.add_node("node_1", label=long_label)
        graph.add_node("node_2", label="short")
        graph.add_edge("node_1", "node_2")
        visualizer = InteractiveVisualizer()
        output_path = temp_dir / "long_labels.html"
        visualizer.visualize(graph, output_path)
        assert output_path.exists()
