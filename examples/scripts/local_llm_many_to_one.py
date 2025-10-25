"""
Example 2: LLM Backend with Many-to-One Processing
===================================================

This example demonstrates document extraction using an LLM backend
with many-to-one processing (entire document processed as one unit).

Use Case:
- Single-entity documents (one invoice, one contract, etc.)
- Documents where context across pages matters
- When you want one cohesive extraction result

Requirements:
- Ollama running locally (for local inference)
- OR Mistral API key (for remote inference)
- llama3:8b-instruct model (or similar)
- A sample document (PDF or image)

Backend: LLM (Language Model)
Processing: Many-to-one (full document)
"""

from pathlib import Path
from docling_graph.pipeline import run_pipeline

# Import template
from ..templates.invoice import Invoice


def main():
    """Extract data from document using LLM backend (many-to-one)"""
    
    print("=" * 70)
    print("EXAMPLE 2: LLM BACKEND - MANY-TO-ONE PROCESSING")
    print("=" * 70)
    
    # Configuration
    source_document = "data/sample_invoice.pdf"  # Change to your document
    
    # Check if document exists
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        print("Please update the 'source_document' path to point to your PDF file")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (Ollama)")
    print("Mode: Many-to-one (full document)")
    
    # Pipeline configuration
    config = {
        # Source document
        "source": source_document,
        
        # Template (as string path or class)
        "template": Invoice,
        
        # Processing mode
        "processing_mode": "many-to-one",  # Process entire document as one
        
        # Backend configuration
        "backend_type": "llm",  # Use LLM backend
        "inference": "local",   # Local inference (Ollama)
        
        # Docling configuration for document preprocessing
        "docling_config": "ocr",  # Use OCR pipeline
        
        # Output configuration
        "output_dir": "outputs/example_02_llm_many_to_one",
        "export_format": "csv",  # Export as CSV (Neo4j compatible)
        "reverse_edges": False,  # Don't create bidirectional edges
        
        # Model configuration
        "config": {
            "models": {
                "llm": {
                    "local": {
                        "default_model": "llama3:8b-instruct",
                        "provider": "ollama"
                    }
                }
            }
        },
        
        # Optional overrides
        "model_override": None,
        "provider_override": None
    }
    
    try:
        print("\n" + "-" * 70)
        print("Running pipeline...")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nOutputs saved to: {config['output_dir']}/")
        print("\nGenerated files:")
        print("  - nodes.csv (graph nodes)")
        print("  - relationships.csv (graph edges)")
        print("  - *_graph.html (interactive visualization)")
        print("  - *_graph.png (static visualization)")
        print("  - *_graph.md (markdown report)")
        
        print("\nTo import into Neo4j:")
        print("  LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row")
        print("  CREATE (n) SET n = row")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR!")
        print("=" * 70)
        print(f"\n{type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure Ollama is running (ollama serve)")
        print("  2. Check that model is available (ollama list)")
        print("  3. Pull model if needed (ollama pull llama3:8b-instruct)")
        print("  4. Verify document path is correct")
        raise


# Alternative: Use remote API instead of local Ollama
def main_remote_api():
    """Same as main() but using Mistral API instead of local Ollama"""
    
    import os
    
    if not os.getenv("MISTRAL_API_KEY"):
        print("MISTRAL_API_KEY not set!")
        print("  Export it: export MISTRAL_API_KEY='your_key_here'")
        return
    
    config = {
        "source": "data/sample_invoice.pdf",
        "template": Invoice,
        "processing_mode": "many-to-one",
        "backend_type": "llm",
        "inference": "remote",  # Use API instead of local
        "docling_config": "ocr",
        "output_dir": "outputs/example_02_llm_many_to_one_remote",
        "export_format": "csv",
        "reverse_edges": False,
        "config": {
            "models": {
                "llm": {
                    "remote": {
                        "default_model": "mistral-large-latest",
                        "provider": "mistral"
                    }
                }
            }
        },
        "provider_override": "mistral"
    }
    
    run_pipeline(config)
    print(f"Completed! Check: {config['output_dir']}/")


if __name__ == "__main__":
    # Choose one:
    main()              # Local Ollama
    # main_remote_api()  # Remote API (uncomment to use)
