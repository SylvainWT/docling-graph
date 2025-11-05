from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from docling_graph.core.extractors.strategies.many_to_one import \
    ManyToOneStrategy
from docling_graph.protocols import (ExtractionBackendProtocol,
                                     TextExtractionBackendProtocol)


# Simple Pydantic model for testing
class MockTemplate(BaseModel):
    name: str
    value: int = 0


# Fixture for a mock LLM backend
@pytest.fixture
def mock_llm_backend():
    backend = MagicMock(spec=TextExtractionBackendProtocol)
    backend.client = MagicMock(context_limit=8000, content_ratio=0.8)
    backend.__class__.__name__ = "MockLlmBackend"

    # Mock extract_from_markdown to return a simple model
    def mock_extract(markdown, template, context, is_partial):
        if "fail" in markdown:
            return None
        return template(name=context, value=len(markdown))

    backend.extract_from_markdown.side_effect = mock_extract

    # Mock consolidation
    def mock_consolidate(raw_models, programmatic_model, template):
        return template(name="Consolidated", value=999)

    backend.consolidate_from_pydantic_models.side_effect = mock_consolidate
    return backend


# Fixture for a mock VLM backend
@pytest.fixture
def mock_vlm_backend():
    backend = MagicMock(spec=ExtractionBackendProtocol)
    backend.__class__.__name__ = "MockVlmBackend"

    def mock_extract(source, template):
        if "single" in source:
            return [template(name="Page 1", value=10)]
        if "multi" in source:
            return [
                template(name="Page 1", value=10),
                template(name="Page 2", value=20),
            ]
        return []

    backend.extract_from_document.side_effect = mock_extract
    return backend


# Patch DocumentProcessor and other dependencies
@pytest.fixture(autouse=True)
def patch_deps():
    with patch(
        "docling_graph.core.extractors.strategies.many_to_one.DocumentProcessor"
    ) as mock_dp, patch(
        "docling_graph.core.extractors.strategies.many_to_one.ChunkBatcher"
    ) as mock_cb, patch(
        "docling_graph.core.extractors.strategies.many_to_one.merge_pydantic_models"
    ) as mock_merge:
        # Configure mocks
        mock_doc_processor = mock_dp.return_value
        mock_doc_processor.convert_to_docling_doc.return_value = "MockDoc"
        mock_doc_processor.extract_chunks.return_value = [
            "chunk1",
            "chunk2",
        ]
        mock_doc_processor.extract_page_markdowns.return_value = [
            "page1_md",
            "page2_md",
        ]
        mock_doc_processor.extract_full_markdown.return_value = "full_doc_md"

        mock_batcher = mock_cb.return_value
        mock_batcher.batch_chunks.return_value = [
            MagicMock(batch_id=0, chunk_count=2, combined_text="chunk1chunk2")
        ]

        # Mock merge to return a combined model
        mock_merge.return_value = MockTemplate(name="Merged", value=123)

        yield mock_dp, mock_cb, mock_merge


def test_init_llm_chunking(mock_llm_backend, patch_deps):
    """Test init with LLM backend and chunking enabled."""
    mock_dp, _, _ = patch_deps
    strategy = ManyToOneStrategy(
        backend=mock_llm_backend, use_chunking=True
    )
    assert strategy.use_chunking is True
    assert strategy.llm_consolidation is False
    # Check DocumentProcessor was initialized with chunker_config
    mock_dp.assert_called_with(
        docling_config="default",
        chunker_config={"max_tokens": 6400},  # 8000 * 0.8
    )


def test_init_vlm(mock_vlm_backend, patch_deps):
    """Test init with VLM backend (chunking is irrelevant)."""
    mock_dp, _, _ = patch_deps
    strategy = ManyToOneStrategy(
        backend=mock_vlm_backend, use_chunking=True
    )
    assert strategy.use_chunking is True
    # Check DocumentProcessor was initialized
    mock_dp.assert_called_with(docling_config="default", chunker_config=None)


def test_extract_with_vlm_single_page(mock_vlm_backend, patch_deps):
    """Test VLM extraction for a single-page document."""
    _, _, mock_merge = patch_deps
    strategy = ManyToOneStrategy(backend=mock_vlm_backend)

    # Use a source path that mock_vlm_backend understands
    results = strategy.extract("single_page_doc.pdf", MockTemplate)

    assert len(results) == 1
    assert results[0].name == "Page 1"
    assert results[0].value == 10
    # Merge should not be called for a single model
    mock_merge.assert_not_called()


def test_extract_with_vlm_multi_page(mock_vlm_backend, patch_deps):
    """Test VLM extraction and merge for a multi-page document."""
    _, _, mock_merge = patch_deps
    strategy = ManyToOneStrategy(backend=mock_vlm_backend)

    results = strategy.extract("multi_page_doc.pdf", MockTemplate)

    # Should return the programmatically merged model
    assert len(results) == 1
    assert results[0].name == "Merged"
    assert results[0].value == 123
    mock_merge.assert_called_once()


@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_vlm_backend",
    return_value=False,
)
@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_llm_backend",
    return_value=True,
)
def test_extract_with_llm_chunking(
    mock_is_llm, mock_is_vlm, mock_llm_backend, patch_deps
):
    """Test the LLM chunking-and-merging strategy."""
    mock_dp, mock_cb, mock_merge = patch_deps
    mock_doc_processor = mock_dp.return_value
    mock_batcher = mock_cb.return_value

    strategy = ManyToOneStrategy(
        backend=mock_llm_backend, use_chunking=True
    )
    results = strategy.extract("source.pdf", MockTemplate)

    # Check call flow
    mock_doc_processor.convert_to_docling_doc.assert_called_with("source.pdf")
    mock_doc_processor.extract_chunks.assert_called_with("MockDoc")
    mock_batcher.batch_chunks.assert_called_with(["chunk1", "chunk2"])
    # Check LLM was called for the batch
    mock_llm_backend.extract_from_markdown.assert_called_with(
        markdown="chunk1chunk2",
        template=MockTemplate,
        context="batch 1 (2 chunks)",
        is_partial=True,
    )
    # Check merge was called
    mock_merge.assert_called_once()
    # Check result is the merged model
    assert len(results) == 1
    assert results[0].name == "Merged"


@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_vlm_backend",
    return_value=False,
)
@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_llm_backend",
    return_value=True,
)
def test_extract_with_llm_consolidation(
    mock_is_llm, mock_is_vlm, mock_llm_backend, patch_deps
):
    """Test LLM chunking with the final LLM consolidation step."""
    strategy = ManyToOneStrategy(
        backend=mock_llm_backend, use_chunking=True, llm_consolidation=True
    )
    results = strategy.extract("source.pdf", MockTemplate)

    # Check that consolidation was called
    mock_llm_backend.consolidate_from_pydantic_models.assert_called_once()
    # Check that the final result is the consolidated one
    assert len(results) == 1
    assert results[0].name == "Consolidated"
    assert results[0].value == 999


@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_vlm_backend",
    return_value=False,
)
@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_llm_backend",
    return_value=True,
)
def test_extract_llm_full_doc_strategy(
    mock_is_llm, mock_is_vlm, mock_llm_backend, patch_deps
):
    """Test fallback to full-doc extraction when chunking is off and doc fits."""
    mock_dp, _, _ = patch_deps
    mock_doc_processor = mock_dp.return_value
    # Make markdown small enough to fit
    mock_doc_processor.extract_full_markdown.return_value = "small doc"

    strategy = ManyToOneStrategy(
        backend=mock_llm_backend, use_chunking=False
    )
    results = strategy.extract("source.pdf", MockTemplate)

    # Check it called full doc extraction
    mock_llm_backend.extract_from_markdown.assert_called_with(
        markdown="small doc",
        template=MockTemplate,
        context="full document",
        is_partial=False,
    )
    assert len(results) == 1
    assert results[0].name == "full document"


@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_vlm_backend",
    return_value=False,
)
@patch(
    "docling_graph.core.extractors.strategies.many_to_one.is_llm_backend",
    return_value=True,
)
def test_extract_llm_page_by_page_strategy(
    mock_is_llm, mock_is_vlm, mock_llm_backend, patch_deps
):
    """Test fallback to page-by-page when chunking is off and doc is too large."""
    mock_dp, _, mock_merge = patch_deps
    mock_doc_processor = mock_dp.return_value
    # Make markdown large enough to not fit
    mock_doc_processor.extract_full_markdown.return_value = "a" * 8000 * 4

    strategy = ManyToOneStrategy(
        backend=mock_llm_backend, use_chunking=False
    )
    results = strategy.extract("source.pdf", MockTemplate)

    # Check it called page-by-page extraction
    mock_doc_processor.extract_page_markdowns.assert_called_with("MockDoc")
    # Check it called extract for each page
    mock_llm_backend.extract_from_markdown.assert_any_call(
        markdown="page1_md",
        template=MockTemplate,
        context="page 1",
        is_partial=True,
    )
    mock_llm_backend.extract_from_markdown.assert_any_call(
        markdown="page2_md",
        template=MockTemplate,
        context="page 2",
        is_partial=True,
    )
    # Check it merged the results
    mock_merge.assert_called_once()
    assert len(results) == 1
    assert results[0].name == "Merged"