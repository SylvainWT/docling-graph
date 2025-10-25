"""
Example 3: LLM Backend with One-to-One Processing
==================================================

This example demonstrates document extraction using an LLM backend
with one-to-one processing (each page processed separately).

Use Case:
- Multi-entity documents (multiple invoices in one PDF)
- Each page contains independent information
- When you want separate extractions per page

Requirements:
- Ollama running locally
- llama3:8b-instruct model (or similar)
- A multi-page document (PDF)

Backend: LLM (Language Model)
Processing: One-to-one (per page)
"""

from pathlib import Path
from docling_graph.pipeline import run_pipeline

# Import template
from ..templates.invoice import Invoice


def main():
    """Extract data from document using LLM backend (one-to-one)"""
    
    print("=" * 70)
    print("EXAMPLE 3: LLM BACKEND - ONE-TO-ONE PROCESSING")
    print("=" * 70)
    
    # Configuration
    source_document = "data/multiple_invoices.pdf"  # Multi-page document
    
    # Check if document exists
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        print("Please update the 'source_document' path")
        print("\nNote: This example works best with multi-page documents")
        print("      where each page contains a separate entity (e.g., invoices)")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (Ollama)")
    print("Mode: One-to-one (per page)")
    print("\nThis will extract one invoice per page and merge into a single graph.")
    
    # Pipeline configuration
    config = {
        # Source document
        "source": source_document,
        
        # Template
        "template": Invoice,
        
        # Processing mode
        "processing_mode": "one-to-one",  # Process each page separately
        
        # Backend configuration
        "backend_type": "llm",
        "inference": "local",
        
        # Docling configuration
        "docling_config": "ocr",
        
        # Output configuration
        "output_dir": "outputs/example_03_llm_one_to_one",
        "export_format": "csv",
        "reverse_edges": False,
        
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
        
        "model_override": None,
        "provider_override": None
    }
    
    try:
        print("\n" + "-" * 70)
        print("Running pipeline...")
        print("Each page will be processed independently...")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nOutputs saved to: {config['output_dir']}/")
        print("\nGenerated files:")
        print("  - nodes.csv (all extracted entities)")
        print("  - relationships.csv (all relationships)")
        print("  - *_graph.html (interactive visualization)")
        print("  - *_graph.png (static visualization)")
        
        print("\n📊 Result:")
        print("  All pages processed separately, results merged into one graph")
        print("  If pages share entities (same customer), they'll be deduplicated")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR!")
        print("=" * 70)
        print(f"\n{type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure Ollama is running")
        print("  2. Verify model is available")
        print("  3. Check document path and format")
        raise


def compare_modes():
    """
    Utility function to compare one-to-one vs many-to-one
    Run both and compare results
    """
    
    print("\n" + "=" * 70)
    print("COMPARING PROCESSING MODES")
    print("=" * 70)
    
    source = "data/sample_document.pdf"
    
    # Run one-to-one
    print("\n1. Running ONE-TO-ONE processing...")
    config_one = {
        "source": source,
        "template": Invoice,
        "processing_mode": "one-to-one",
        "backend_type": "llm",
        "inference": "local",
        "docling_config": "ocr",
        "output_dir": "outputs/compare/one_to_one",
        "export_format": "csv",
        "reverse_edges": False,
        "config": {
            "models": {
                "llm": {
                    "local": {
                        "default_model": "llama3:8b-instruct",
                        "provider": "ollama"
                    }
                }
            }
        }
    }
    
    try:
        run_pipeline(config_one)
        print("One-to-one completed")
    except Exception as e:
        print(f"One-to-one failed: {e}")
    
    # Run many-to-one
    print("\n2. Running MANY-TO-ONE processing...")
    config_many = config_one.copy()
    config_many.update({
        "processing_mode": "many-to-one",
        "output_dir": "outputs/compare/many_to_one"
    })
    
    try:
        run_pipeline(config_many)
        print("Many-to-one completed")
    except Exception as e:
        print(f"Many-to-one failed: {e}")
    
    print("\n" + "=" * 70)
    print("COMPARISON COMPLETE")
    print("=" * 70)
    print("\nCheck outputs in:")
    print("  - outputs/compare/one_to_one/")
    print("  - outputs/compare/many_to_one/")
    
    print("\nKey differences:")
    print("  One-to-one: Better for multi-entity documents")
    print("  Many-to-one: Better for single entity with multi-page context")


if __name__ == "__main__":
    # Choose one:
    main()           # Run one-to-one example
    # compare_modes()  # Compare both modes (uncomment to use)
