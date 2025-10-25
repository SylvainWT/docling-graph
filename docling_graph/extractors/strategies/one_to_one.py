"""
One-to-one extraction strategy.
Processes each page independently and returns multiple models.
"""

from pydantic import BaseModel
from typing import Type, List
from rich import print

from ...protocols import is_vlm_backend, is_llm_backend, get_backend_type
from ..document_processor import DocumentProcessor
from ..extractor_base import BaseExtractor


class OneToOneStrategy(BaseExtractor):
    """One-to-one extraction strategy.

    Extracts one model per page/item using Protocol-based type checking.
    """

    def __init__(self, backend, docling_config: str = "default"):
        """Initialize with a backend (VlmBackend or LlmBackend).

        Args:
            backend: Extraction backend instance implementing either
                     ExtractionBackendProtocol or TextExtractionBackendProtocol.
            docling_config: Docling pipeline configuration ('ocr' or 'vision').
        """
        self.backend = backend
        self.doc_processor = DocumentProcessor(docling_config=docling_config)

        backend_type = get_backend_type(backend)
        print(f"[blue][OneToOneStrategy][/blue] Initialized with {backend_type.upper()} backend: "
              f"[cyan]{backend.__class__.__name__}[/cyan]")

    def extract(self, source: str, template: Type[BaseModel]) -> List[BaseModel]:
        """Extract data using one-to-one strategy.

        For VLM: Uses direct VLM extraction (already page-based).
        For LLM: Converts to markdown and processes each page separately.

        Args:
            source: Path to the source document.
            template: Pydantic model template to extract into.

        Returns:
            List of extracted Pydantic model instances (one per page).
        """
        # Use Protocol-based type checking instead of string comparison
        if is_vlm_backend(self.backend):
            # VLM backend handles page-based extraction natively
            return self.backend.extract_from_document(source, template)

        elif is_llm_backend(self.backend):
            # LLM backend: convert document and process each page
            document = self.doc_processor.convert_to_markdown(source)
            page_markdowns = self.doc_processor.extract_page_markdowns(document)

            extracted_models = []
            for page_num, page_md in enumerate(page_markdowns, 1):
                print(f"[blue][OneToOneStrategy][/blue] Processing page {page_num}/{len(page_markdowns)}")

                model = self.backend.extract_from_markdown(
                    markdown=page_md,
                    template=template,
                    context=f"page {page_num}"
                )

                if model:
                    extracted_models.append(model)

            print(f"[blue][OneToOneStrategy][/blue] Extracted {len(extracted_models)} model(s)")
            return extracted_models

        else:
            # This shouldn't happen if backend implements a protocol correctly
            backend_class = self.backend.__class__.__name__
            raise TypeError(
                f"Backend {backend_class} does not implement required protocols. "
                f"Must implement either ExtractionBackendProtocol or TextExtractionBackendProtocol."
            )
