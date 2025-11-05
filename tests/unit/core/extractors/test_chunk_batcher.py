import pytest
from unittest.mock import MagicMock, patch

from docling_graph.core.extractors.chunk_batcher import ChunkBatcher


@pytest.fixture
def mock_tokenizer():
    """Mock tokenizer that counts tokens as 1 per word."""
    tok = MagicMock()

    def count_tokens(text: str):
        return len(text.split())

    tok.apply_chat_template.return_value = []
    tok.count_tokens.side_effect = count_tokens
    return tok


@patch("docling_graph.core.extractors.chunk_batcher.AutoTokenizer.from_pretrained")
def test_batcher_init(mock_from_pretrained, mock_tokenizer):
    """Test batcher initialization."""
    mock_from_pretrained.return_value = mock_tokenizer
    batcher = ChunkBatcher(
        context_limit=4096,
        system_prompt_tokens=100,
        response_buffer_tokens=200,
    )
    assert batcher.max_content_tokens == 3796  # 4096 - 100 - 200
    assert batcher.tokenizer == mock_tokenizer


@patch("docling_graph.core.extractors.chunk_batcher.AutoTokenizer.from_pretrained")
def test_batch_chunks_simple(mock_from_pretrained, mock_tokenizer):
    """Test a simple case where all chunks fit in one batch."""
    mock_from_pretrained.return_value = mock_tokenizer
    # 1000 tokens total budget
    batcher = ChunkBatcher(context_limit=1500, system_prompt_tokens=250, response_buffer_tokens=250)
    assert batcher.max_content_tokens == 1000
    
    chunks = ["word " * 200, "word " * 300, "word " * 400] # 200 + 300 + 400 = 900 tokens
    
    batches = batcher.batch_chunks(chunks)
    
    assert len(batches) == 1
    assert batches[0].batch_id == 0
    assert batches[0].chunk_count == 3
    assert batches[0].token_count == 900
    assert batches[0].combined_text == "\n\n---\n\n".join(chunks)


@patch("docling_graph.core.extractors.chunk_batcher.AutoTokenizer.from_pretrained")
def test_batch_chunks_multiple_batches(mock_from_pretrained, mock_tokenizer):
    """Test splitting chunks across multiple batches."""
    mock_from_pretrained.return_value = mock_tokenizer
    # 500 tokens budget
    batcher = ChunkBatcher(context_limit=1000, system_prompt_tokens=250, response_buffer_tokens=250)
    assert batcher.max_content_tokens == 500

    chunks = [
        "word " * 400,  # Batch 1 (400)
        "word " * 300,  # Batch 2 (300)
        "word " * 450,  # Batch 2 (300 + 450 > 500) -> No, 300 + 450 = 750. So Batch 2 (300)
        "word " * 450,  # Batch 3 (450)
    ]

    batches = batcher.batch_chunks(chunks)

    assert len(batches) == 3
    # Batch 1
    assert batches[0].batch_id == 0
    assert batches[0].chunk_count == 1
    assert batches[0].token_count == 400
    # Batch 2
    assert batches[1].batch_id == 1
    assert batches[1].chunk_count == 1
    assert batches[1].token_count == 300
    # Batch 3
    assert batches[2].batch_id == 2
    assert batches[2].chunk_count == 1
    assert batches[2].token_count == 450

@patch("docling_graph.core.extractors.chunk_batcher.AutoTokenizer.from_pretrained")
def test_batch_chunks_merge_threshold(mock_from_pretrained, mock_tokenizer):
    """Test that a small chunk gets merged into the previous batch."""
    mock_from_pretrained.return_value = mock_tokenizer
    # 500 tokens budget, 85% merge threshold (425 tokens)
    batcher = ChunkBatcher(
        context_limit=1000,
        system_prompt_tokens=250,
        response_buffer_tokens=250,
        merge_threshold=0.85,
    )
    assert batcher.max_content_tokens == 500
    
    chunks = [
        "word " * 400,  # Batch 1 (400 tokens)
        "word " * 50,   # This is < (500 * (1-0.85)) = 75 tokens, so it should merge
    ]

    batches = batcher.batch_chunks(chunks)
    
    assert len(batches) == 1
    assert batches[0].chunk_count == 2
    assert batches[0].token_count == 450 # 400 + 50


@patch("docling_graph.core.extractors.chunk_batcher.AutoTokenizer.from_pretrained")
def test_batch_chunks_single_large_chunk(mock_from_pretrained, mock_tokenizer):
    """Test that a chunk larger than the limit is put in its own batch."""
    mock_from_pretrained.return_value = mock_tokenizer
    # 500 tokens budget
    batcher = ChunkBatcher(context_limit=1000, system_prompt_tokens=250, response_buffer_tokens=250)
    assert batcher.max_content_tokens == 500
    
    chunks = [
        "word " * 700,  # Batch 1 (700) - Over budget, but becomes its own batch
        "word " * 200,  # Batch 2 (200)
    ]
    
    batches = batcher.batch_chunks(chunks)
    
    assert len(batches) == 2
    # Batch 1
    assert batches[0].batch_id == 0
    assert batches[0].chunk_count == 1
    assert batches[0].token_count == 700
    # Batch 2
    assert batches[1].batch_id == 1
    assert batches[1].chunk_count == 1
    assert batches[1].token_count == 200