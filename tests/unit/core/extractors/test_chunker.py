import pytest
from unittest.mock import MagicMock, patch

from docling_graph.core.extractors.chunker import DocumentChunker


@pytest.fixture
def mock_tokenizer_instance():
    """Mock tokenizer instance."""
    tok = MagicMock()
    tok.count_tokens.return_value = 10
    return tok


@pytest.fixture
def mock_tokenizer_class(mock_tokenizer_instance):
    """Mock tokenizer class (AutoTokenizer)."""
    cls = MagicMock()
    cls.from_pretrained.return_value = mock_tokenizer_instance
    return cls


@pytest.fixture
def mock_hybrid_chunker_instance():
    """Mock HybridChunker instance."""
    chunker = MagicMock()
    chunker.chunk_document.return_value = ["chunk1", "chunk2"]
    return chunker


@pytest.fixture
def mock_hybrid_chunker_class(mock_hybrid_chunker_instance):
    """Mock HybridChunker class."""
    cls = MagicMock()
    cls.return_value = mock_hybrid_chunker_instance
    return cls


# Patch dependencies for all tests
@pytest.fixture(autouse=True)
def patch_dependencies(mock_tokenizer_class, mock_hybrid_chunker_class):
    with patch(
        "docling_graph.core.extractors.chunker.AutoTokenizer", mock_tokenizer_class
    ), patch(
        "docling_graph.core.extractors.chunker.HybridChunker", mock_hybrid_chunker_class
    ):
        yield


def test_chunker_init_with_tokenizer_name(
    mock_tokenizer_class, mock_hybrid_chunker_class
):
    """Test initialization with a specific tokenizer name."""
    config = {
        "tokenizer_name": "test-model",
        "max_tokens": 1024,
        "merge_peers": False,
    }
    chunker = DocumentChunker(**config)

    mock_tokenizer_class.from_pretrained.assert_called_with("test-model")
    mock_hybrid_chunker_class.assert_called_with(
        tokenizer=mock_tokenizer_class.from_pretrained.return_value,
        max_chunk_tokens=1024,
        merge_peers=False,
    )
    assert chunker.tokenizer_name == "test-model"


def test_chunker_init_with_provider(mock_tokenizer_class, mock_hybrid_chunker_class):
    """Test initialization using a provider shortcut."""
    config = {"provider": "mistral", "max_tokens": 2048}
    chunker = DocumentChunker(**config)

    # Check it resolved to the correct tokenizer name
    expected_name = "mistralai/Mistral-7B-Instruct-v0.2"
    mock_tokenizer_class.from_pretrained.assert_called_with(expected_name)
    mock_hybrid_chunker_class.assert_called_with(
        tokenizer=mock_tokenizer_class.from_pretrained.return_value,
        max_chunk_tokens=2048,
        merge_peers=True,  # Default for provider
    )
    assert chunker.tokenizer_name == expected_name


def test_chunk_document(mock_hybrid_chunker_instance):
    """Test the chunk_document method."""
    chunker = DocumentChunker(max_tokens=1024)
    mock_doc = MagicMock()
    chunks = chunker.chunk_document(mock_doc)

    assert chunks == ["chunk1", "chunk2"]
    mock_hybrid_chunker_instance.chunk_document.assert_called_with(mock_doc)


def test_chunk_document_with_stats(mock_hybrid_chunker_instance, mock_tokenizer_instance):
    """Test the stats-enabled chunking method."""
    chunker = DocumentChunker(max_tokens=1024)
    mock_doc = MagicMock()

    # Configure mock tokenizer to return different counts
    mock_tokenizer_instance.count_tokens.side_effect = [150, 250]  # Tokens for chunk1, chunk2
    # Configure hybrid chunker
    mock_hybrid_chunker_instance.chunk_document.return_value = [
        "This is chunk 1",
        "This is chunk 2, it is longer",
    ]

    chunks, stats = chunker.chunk_document_with_stats(mock_doc)

    assert chunks == ["This is chunk 1", "This is chunk 2, it is longer"]
    assert stats["total_chunks"] == 2
    assert stats["total_tokens"] == 400  # 150 + 250
    assert stats["avg_tokens"] == 200.0
    assert stats["max_tokens_in_chunk"] == 250
    assert stats["min_tokens_in_chunk"] == 150


def test_get_config_summary():
    """Test the configuration summary string."""
    chunker = DocumentChunker(
        tokenizer_name="test-model", max_tokens=1234, merge_peers=True
    )
    summary = chunker.get_config_summary()
    assert "test-model" in summary
    assert "1234" in summary
    assert "merge_peers=True" in summary