"""
Example 4: VLM Backend with One-to-One Processing
==================================================

This example demonstrates document extraction using a Vision-Language Model (VLM)
backend with one-to-one processing (each page processed separately).

Use Case:
- Visual documents with complex layouts (forms, receipts, IDs)
- Multi-page documents where each page is independent
- When you need vision-based understanding (not just OCR)

Requirements:
- Docling with VLM support installed: pip install docling[vlm]
- GPU recommended (but works on CPU)
- numind/NuExtract-2.0-8B model (downloads automatically on first run)
- A multi-page document (PDF or images)

Backend: VLM (Vision-Language Model)
Processing: One-to-one (per page)
Docling Config: vision (VLM pipeline)

Note: VLM backend is LOCAL-ONLY. Remote API inference is not supported.
"""

from pathlib import Path
from docling_graph.pipeline import run_pipeline

# Import template
from templates import IdentityDocument


def main():
    """Extract data from document using VLM backend (one-to-one)"""
    
    print("=" * 70)
    print("EXAMPLE 4: VLM BACKEND - ONE-TO-ONE PROCESSING")
    print("=" * 70)
    
    # Configuration
    source_document = "data/id_cards.pdf"  # Multi-page document with ID cards
    
    # Check if document exists
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        print("Please update the 'source_document' path")
        print("\nNote: VLM works best with:")
        print("  - Visual documents (ID cards, receipts, forms)")
        print("  - Complex layouts that OCR might struggle with")
        print("  - Documents where image understanding is important")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: IdentityDocument")
    print("Backend: VLM (Vision-Language Model)")
    print("Mode: One-to-one (per page)")
    print("Docling Config: vision (VLM pipeline)")
    print("\nEach page will be processed separately using vision understanding.")
    
    # Pipeline configuration
    config = {
        # Source document
        "source": source_document,
        
        # Template
        "template": "templates.IdentityDocument",
        
        # Processing mode
        "processing_mode": "one-to-one",  # Process each page separately
        
        # Backend configuration
        "backend_type": "vlm",  # Use VLM backend
        "inference": "local",   # VLM is local-only
        
        # Docling configuration - MUST use "vision" for VLM backend
        "docling_config": "vision",  # Use VLM pipeline (not OCR)
        
        # Output configuration
        "output_dir": "outputs/example_04_vlm_one_to_one",
        "export_format": "csv",
        "reverse_edges": False,
        
        # Model configuration
        "config": {
            "models": {
                "vlm": {
                    "local": {
                        "default_model": "numind/NuExtract-2.0-8B",  # HuggingFace repo
                        "provider": "docling"
                    }
                }
            }
        },
        
        "model_override": None,
        "provider_override": None
    }
    
    try:
        print("\n" + "-" * 70)
        print("Initializing VLM backend...")
        print("(First run will download the model - this may take a few minutes)")
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
        print("  Each page processed separately using vision understanding")
        print("  Results merged into one unified graph")
        print("  VLM can understand layout, handwriting, and visual context")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR!")
        print("=" * 70)
        print(f"\n{type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Install VLM support: pip install docling[vlm]")
        print("  2. Check GPU availability (recommended but not required)")
        print("  3. Ensure sufficient disk space for model download (~4-8GB)")
        print("  4. For CPU-only: set CUDA_VISIBLE_DEVICES='' before running")
        print("  5. Try smaller model: numind/NuExtract-2.0-2B")
        raise


def use_different_vlm_model():
    """
    Example using a different (smaller/faster) VLM model
    """
    
    print("\n" + "=" * 70)
    print("USING SMALLER VLM MODEL")
    print("=" * 70)
    
    config = {
        "source": "data/id_card.pdf",
        "template": "templates.IdentityDocument",
        "processing_mode": "one-to-one",
        "backend_type": "vlm",
        "inference": "local",
        "docling_config": "vision",
        "output_dir": "outputs/example_04_vlm_small_model",
        "export_format": "csv",
        "reverse_edges": False,
        "config": {
            "models": {
                "vlm": {
                    "local": {
                        # Smaller, faster model (2B vs 8B parameters)
                        "default_model": "numind/NuExtract-2.0-2B",
                        "provider": "docling"
                    }
                }
            }
        }
    }
    
    try:
        print("\nUsing smaller model: numind/NuExtract-2.0-2B")
        print("  - Faster inference")
        print("  - Lower memory usage")
        print("  - Slightly less accurate\n")
        
        run_pipeline(config)
        print(f"\nCompleted! Check: {config['output_dir']}/")
        
    except Exception as e:
        print(f"\nFailed: {e}")


def gpu_memory_optimization():
    """
    Tips for running VLM with limited GPU memory
    """
    print("\n" + "=" * 70)
    print("GPU MEMORY OPTIMIZATION TIPS")
    print("=" * 70)
    
    print("""
VLM models can be memory-intensive. Here are optimization strategies:

1. Use smaller model:
   - numind/NuExtract-2.0-2B (2B params, ~4GB GPU)
   - numind/NuExtract-2.0-8B (8B params, ~8GB GPU)

2. Process fewer pages at once:
   - Split large PDFs into smaller chunks
   - Process one document at a time

3. Clear GPU cache between runs:
   import torch
   torch.cuda.empty_cache()

4. Run on CPU (slower but works):
   export CUDA_VISIBLE_DEVICES=""
   python ex04_vlm_one_to_one.py

5. Use mixed precision (automatic in docling):
   - Model automatically uses FP16/BF16 on compatible GPUs

6. Monitor GPU usage:
   watch -n 1 nvidia-smi

7. Batch processing strategy:
   - Process documents sequentially
   - Clean up memory between documents
   - See ex06_batch_processing.py for implementation
""")


def vlm_vs_llm_comparison():
    """
    When to use VLM vs LLM backend
    """
    print("\n" + "=" * 70)
    print("VLM vs LLM: WHEN TO USE EACH")
    print("=" * 70)
    
    print("""
Use VLM Backend when:
---------------------
Document has complex visual layout
Need to understand spatial relationships
Dealing with handwriting or signatures
Forms, tables, receipts, ID cards
Mixed text and visual elements
OCR quality is poor or unreliable

Use LLM Backend when:
--------------------
Document is text-heavy
Clean, well-formatted documents
Long documents (multi-page reports)
Need semantic understanding of text
Better at reasoning and inference
Can use remote APIs (cheaper/faster)

Performance Comparison:
----------------------
VLM:
  - Better: Visual understanding
  - Slower: GPU-intensive
  - Local only
  - Higher memory usage

LLM:
  - Better: Text reasoning
  - Faster: Especially with APIs
  - Local or remote
  - Lower memory usage
  - Better for long documents

Recommendation:
--------------
- Try VLM first for visual documents
- Fall back to LLM if VLM struggles or memory is limited
- Use LLM for text-heavy documents
- Combine both: VLM for extraction + LLM for reasoning
""")


if __name__ == "__main__":
    import sys
    
    print("\nVLM Backend Example - One-to-One Processing")
    print("=" * 70)
    print("\nChoose an option:")
    print("1. Run VLM extraction (default model)")
    print("2. Run with smaller/faster model")
    print("3. Show GPU optimization tips")
    print("4. Show VLM vs LLM comparison")
    
    choice = input("\nEnter your choice (1-4, default=1): ").strip() or "1"
    
    if choice == "1":
        main()
    elif choice == "2":
        use_different_vlm_model()
    elif choice == "3":
        gpu_memory_optimization()
    elif choice == "4":
        vlm_vs_llm_comparison()
    else:
        print("Invalid choice!")
        sys.exit(1)
