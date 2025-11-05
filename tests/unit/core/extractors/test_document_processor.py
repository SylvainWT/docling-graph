from unittest.mock import MagicMock, patch

import pytest
from docling.document_converter import DocumentConverter

from docling_graph.core.extractors.chunker import DocumentChunker
from docling_graph.core.extractors.document_processor import DocumentProcessor


# Mock DoclingDocument to avoid real docling dependency
@pytest.fixture
def mock_docling_doc():
    doc = MagicMock()
    doc.pages = {1: "page1", 2: "page2"}
    doc.export_to_markdown.return_value = "Full Markdown"
    return doc


# Patch the DocumentConverter and DocumentChunker during tests
@pytest.fixture(autouse=True)
def patch_dependencies():
    with patch(
        "docling_graph.core.extractors.document_processor.DocumentConverter",
        spec=DocumentConverter,
    ) as mock_converter, patch(
        "docling_graph.core.extractors.document_processor.DocumentChunker",
        spec=DocumentChunker,
    ) as mock_chunker:
        # Configure the mock converter instance
        mock_converter_instance = mock_converter.return_value
        mock_converter_instance.convert.return_value = MagicMock(
            document="MockDoc"
        )
        # Configure the mock chunker instance
        mock_chunker_instance = mock_chunker.return_value
        mock_chunker_instance.chunk_document.return_value = [
            "chunk1",
            "chunk2",
        ]
        mock_chunker_instance.chunk_document_with_stats.return_value = (
            ["chunk1", "chunk2"],
            {"total_chunks": 2, "avg_tokens": 10, "max_tokens_in_chunk": 12},
        )
        mock_chunker_instance.get_config_summary.return_value = "Mock Chunker Config"

        yield mock_converter, mock_chunker


def test_init_default_ocr(patch_dependencies):
    """Test default 'ocr' initialization."""
    mock_converter, _ = patch_dependencies
    processor = DocumentProcessor(docling_config="ocr")

    assert processor.docling_config == "ocr"
    assert processor.chunker is None
    # Check that DocumentConverter was initialized
    mock_converter.assert_called_once()


def test_init_vision(patch_dependencies):
    """Test 'vision' initialization."""
    mock_converter, _ = patch_dependencies
    processor = DocumentProcessor(docling_config="vision")

    assert processor.docling_config == "vision"
    assert processor.chunker is None
    # Check that DocumentConverter was initialized
    mock_converter.assert_called_once()


def test_init_with_chunker(patch_dependencies):
    """Test initialization with chunker configuration."""
    _, mock_chunker = patch_dependencies
    chunker_config = {"max_tokens": 4096}
    processor = DocumentProcessor(chunker_config=chunker_config)

    assert processor.chunker is not None
    # Check that DocumentChunker was initialized with the config
    mock_chunker.assert_called_with(**chunker_config)


def test_convert_to_docling_doc(patch_dependencies):
    """Test document conversion call."""
    mock_converter, _ = patch_dependencies
    mock_converter_instance = mock_converter.return_value

    processor = DocumentProcessor()
    doc = processor.convert_to_docling_doc("source/path")

    # Check that the converter's convert method was called
    mock_converter_instance.convert.assert_called_with("source/path")
    # Check that it returned the document part of the result
    assert doc == "MockDoc"


def test_extract_page_markdowns(mock_docling_doc):
    """Test extracting markdown page by page."""
    processor = DocumentProcessor()

    # Configure mock doc
    def export_side_effect(page_no=None):
        if page_no == 1:
            return "Page 1 MD"
        if page_no == 2:
            return "Page 2 MD"
        return "Full MD"

    mock_docling_doc.export_to_markdown.side_effect = export_side_effect

    markdowns = processor.extract_page_markdowns(mock_docling_doc)

    assert markdowns == ["Page 1 MD", "Page 2 MD"]
    # Check calls
    mock_docling_doc.export_to_markdown.assert_any_call(page_no=1)
    mock_docling_doc.export_to_markdown.assert_any_call(page_no=2)


def test_extract_full_markdown(mock_docling_doc):
    """Test extracting the full document markdown."""
    processor = DocumentProcessor()
    md = processor.extract_full_markdown(mock_docling_doc)

    assert md == "Full Markdown"
    # Check it was called with no page_no
    mock_docling_doc.export_to_markdown.assert_called_with()


def test_extract_chunks_no_chunker_raises_error():
    """Test that extract_chunks fails if chunker is not configured."""
    processor = DocumentProcessor()  # No chunker_config
    with pytest.raises(
        ValueError, match="Chunker not initialized"
    ):
        processor.extract_chunks(MagicMock())


def test_extract_chunks_no_stats(patch_dependencies):
    """Test extract_chunks without stats."""
    _, mock_chunker = patch_dependencies
    processor = DocumentProcessor(chunker_config={"max_tokens": 1024})

    chunks = processor.extract_chunks(MagicMock(), with_stats=False)

    assert chunks == ["chunk1", "chunk2"]
    processor.chunker.chunk_document.assert_called_once()


def test_extract_chunks_with_stats(patch_dependencies):
    """Test extract_chunks with stats."""
    _, mock_chunker = patch_dependencies
    processor = DocumentProcessor(chunker_config={"max_tokens": 1024})

    chunks, stats = processor.extract_chunks(MagicMock(), with_stats=True)

    assert chunks == ["chunk1", "chunk2"]
    assert stats["total_chunks"] == 2
    processor.chunker.chunk_document_with_stats.assert_called_once()


@patch.object(
    DocumentProcessor,
    "convert_to_docling_doc",
    return_value=MagicMock(),
)
@patch.object(DocumentProcessor, "extract_page_markdowns")
def test_process_document(
    mock_extract_pages, mock_convert, mock_docling_doc
):
    """Test the high-level process_document helper."""
    # Re-assign mock_docling_doc to the return value of the patched convert
    mock_convert.return_value = mock_docling_doc
    mock_extract_pages.return_value = ["Page 1 MD", "Page 2 MD"]

    processor = DocumentProcessor()
    markdowns = processor.process_document("source/path")

    # Check the internal calls
    mock_convert.assert_called_with("source/path")
    mock_extract_pages.assert_called_with(mock_docling_doc)
    assert markdowns == ["Page 1 MD", "Page 2 MD"]


@patch.object(
    DocumentProcessor,
    "convert_to_docling_doc",
    return_value=MagicMock(),
)
@patch.object(DocumentProcessor, "extract_chunks")
def test_process_document_with_chunking(
    mock_extract_chunks, mock_convert, mock_docling_doc
):
    """Test the high-level chunking processor."""
    mock_convert.return_value = mock_docling_doc
    mock_extract_chunks.return_value = ["chunk1", "chunk2"]

    # Must init with chunker config to enable chunking
    processor = DocumentProcessor(chunker_config={"max_tokens": 1024})
    chunks = processor.process_document_with_chunking("source/path")

    # Check the internal calls
    mock_convert.assert_called_with("source/path")
    mock_extract_chunks.assert_called_with(mock_docling_doc)
    assert chunks == ["chunk1", "chunk2"]