import pytest
from unittest.mock import MagicMock, patch

from docling_graph.config import (
    PipelineConfig,
    ExtractorConfig,
    BackendConfig,
)
from docling_graph.core.extractors.factory import ExtractorFactory
from docling_graph.core.extractors.strategies.many_to_one import ManyToOneStrategy
from docling_graph.core.extractors.strategies.one_to_one import OneToOneStrategy
from docling_graph.core.extractors.backends.llm_backend import LlmBackend
from docling_graph.core.extractors.backends.vlm_backend import VlmBackend


# Patch all external dependencies (client and backend classes)
@pytest.fixture(autouse=True)
def patch_dependencies():
    with patch(
        "docling_graph.core.extractors.factory.LlmBackend", spec=LlmBackend
    ) as mock_llm_be, patch(
        "docling_graph.core.extractors.factory.VlmBackend", spec=VlmBackend
    ) as mock_vlm_be, patch(
        "docling_graph.core.extractors.factory.ManyToOneStrategy", spec=ManyToOneStrategy
    ) as mock_mto, patch(
        "docling_graph.core.extractors.factory.OneToOneStrategy", spec=OneToOneStrategy
    ) as mock_oto, patch(
        "docling_graph.core.extractors.factory.LLM_CLIENT_MAP",
        {
            "ollama": MagicMock(),
            "mistral": MagicMock(),
        },
    ), patch(
        "docling_graph.core.extractors.factory.VLM_CLIENT_MAP",
        {"docling_vlm": MagicMock()},
    ):
        yield {
            "LlmBackend": mock_llm_be,
            "VlmBackend": mock_vlm_be,
            "ManyToOneStrategy": mock_mto,
            "OneToOneStrategy": mock_oto,
        }


def test_create_llm_backend():
    """Test creating an LLM backend."""
    config = BackendConfig(provider="ollama", model="llama3")
    factory = ExtractorFactory()
    backend = factory.create_backend(config)

    assert isinstance(backend, LlmBackend)


def test_create_vlm_backend():
    """Test creating a VLM backend."""
    config = BackendConfig(provider="docling_vlm", model="docling-model")
    factory = ExtractorFactory()
    backend = factory.create_backend(config)

    assert isinstance(backend, VlmBackend)


def test_create_unknown_backend_raises_error():
    """Test that an unknown provider raises a ValueError."""
    config = BackendConfig(provider="unknown_provider", model="test")
    factory = ExtractorFactory()

    with pytest.raises(ValueError, match="Unknown backend provider"):
        factory.create_backend(config)


def test_create_many_to_one_strategy(patch_dependencies):
    """Test creating a ManyToOneStrategy."""
    mock_backend = MagicMock(spec=LlmBackend)
    config = ExtractorConfig(
        strategy="many-to-one",
        docling_config="ocr",
        use_chunking=True,
        llm_consolidation=True,
    )
    factory = ExtractorFactory()
    strategy = factory.create_strategy(mock_backend, config)

    patch_dependencies["ManyToOneStrategy"].assert_called_with(
        backend=mock_backend,
        docling_config="ocr",
        use_chunking=True,
        llm_consolidation=True,
        chunker_config=None,  # Not specified in this config
    )
    assert isinstance(strategy, ManyToOneStrategy)


def test_create_one_to_one_strategy(patch_dependencies):
    """Test creating a OneToOneStrategy."""
    mock_backend = MagicMock(spec=VlmBackend)
    config = ExtractorConfig(
        strategy="one-to-one", docling_config="vision"
    )
    factory = ExtractorFactory()
    strategy = factory.create_strategy(mock_backend, config)

    patch_dependencies["OneToOneStrategy"].assert_called_with(
        backend=mock_backend, docling_config="vision"
    )
    assert isinstance(strategy, OneToOneStrategy)


def test_create_unknown_strategy_raises_error():
    """Test that an unknown strategy raises a ValueError."""
    config = ExtractorConfig(strategy="unknown_strategy")
    factory = ExtractorFactory()

    with pytest.raises(ValueError, match="Unknown strategy type"):
        factory.create_strategy(MagicMock(), config)


@patch.object(ExtractorFactory, "create_backend")
@patch.object(ExtractorFactory, "create_strategy")
def test_create_from_config(
    mock_create_strategy, mock_create_backend, patch_dependencies
):
    """Test the main create_from_config entrypoint."""
    # Define a full pipeline config
    config = PipelineConfig(
        backend=BackendConfig(provider="ollama", model="llama3"),
        extractor=ExtractorConfig(
            strategy="many-to-one",
            docling_config="ocr",
            use_chunking=True,
            chunker_config={"max_tokens": 4096},
        ),
    )

    factory = ExtractorFactory()
    strategy = factory.create_from_config(config)

    # Check that create_backend was called with the backend config
    mock_create_backend.assert_called_with(config.backend)
    
    # Check that create_strategy was called with the created backend and extractor config
    mock_create_strategy.assert_called_with(
        mock_create_backend.return_value, config.extractor
    )
    
    # Check that the final returned value is the strategy
    assert strategy == mock_create_strategy.return_value