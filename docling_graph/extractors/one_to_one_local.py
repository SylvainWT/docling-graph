from docling.datamodel.base_models import InputFormat
from docling.document_extractor import DocumentExtractor, ExtractionFormatOption
from docling.pipeline.extraction_vlm_pipeline import ExtractionVlmPipeline
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from rich import print
from .base import BaseExtractor
from pydantic import BaseModel, ValidationError  # Import ValidationError

class OneToOneLocalExtractor(BaseExtractor):
    """
    Extractor for a single document page to a single structured object, using local models.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        try:
            # 1. Get default options from the VLM pipeline class
            pipeline_options = ExtractionVlmPipeline.get_default_options()

            # 2. Set the model repository ID from the input argument
            pipeline_options.vlm_options.repo_id = self.model_name

            # 3. Define custom format options for PDF and IMAGE inputs
            custom_format_options = {
                InputFormat.PDF: ExtractionFormatOption(
                    pipeline_cls=ExtractionVlmPipeline,
                    backend=PyPdfiumDocumentBackend,
                    pipeline_options=pipeline_options
                ),
                InputFormat.IMAGE: ExtractionFormatOption(
                    pipeline_cls=ExtractionVlmPipeline,
                    backend=PyPdfiumDocumentBackend,
                    pipeline_options=pipeline_options
                )
            }

            # 4. Initialize the DocumentExtractor with these specific configurations
            self.extractor = DocumentExtractor(
                allowed_formats=[InputFormat.IMAGE, InputFormat.PDF],
                extraction_format_options=custom_format_options
            )
            
            print(f"[OneToOneLocalExtractor] Initialized with model: [blue]{self.model_name}[/blue]")

        except Exception as e:
            print(f"[OneToOneLocalExtractor] Error during initialization: {e}")
            raise ValueError(f"Failed to initialize extractor: {e}")

    def extract(self, file_path: str, pydantic_object: type[BaseModel]) -> BaseModel | None:
        """
        Extracts data from a single page document and maps it to a Pydantic object.
        """
        try:
            # Use the source/template arguments for the extract method
            result = self.extractor.extract(
                source=file_path,
                template=pydantic_object, # Pass the Pydantic class as the template
            )

            # Check if data was extracted
            if result.pages and result.pages[0].extracted_data:
                raw_data = result.pages[0].extracted_data
                
                try:
                    # --- THIS IS THE VALIDATION STEP ---
                    validated_model = pydantic_object.model_validate(raw_data)
                    return validated_model
                
                except ValidationError as e:
                    # --- NEW: Specific Error Handling ---
                    print(f"[OneToOneLocalExtractor] [red]Validation Error:[/red] The data extracted by the VLM does not match your Pydantic template.")
                    print("[red]Details:[/red]")
                    # Print a simplified, readable version of the Pydantic error
                    for error in e.errors():
                        # 'loc' gives the path to the bad field, e.g., ('line_items', 0, 'description')
                        loc = " -> ".join(map(str, error['loc']))
                        print(f"  - [bold magenta]{loc}[/bold magenta]: [red]{error['msg']}[/red]")
                    
                    print(f"\n[yellow]Extracted Data (raw):[/yellow]\n{raw_data}\n")
                    return None # Explicitly return None on validation failure

            else:
                print(f"[OneToOneLocalExtractor] No data extracted from {file_path}")
                return None
                
        except Exception as e:
            # General errors (e.g., file not found, model crash)
            print(f"[OneToOneLocalExtractor] [red]Critical Error during extraction:[/red] {e}")
            return None

