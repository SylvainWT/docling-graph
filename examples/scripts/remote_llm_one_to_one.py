"""
Example 7: Remote LLM API with One-to-One Processing
=====================================================

This example demonstrates document extraction using remote LLM APIs
(Mistral, OpenAI, Gemini) with one-to-one processing (per page).

Use Case:
- Multi-page documents with separate entities per page
- Fast parallel processing with remote APIs
- Multiple invoices/contracts in one PDF
- Production batch workflows

Requirements:
- API key for one of: Mistral, OpenAI, or Gemini
- Multi-page document with separate entities per page

Backend: LLM (Language Model)
Inference: Remote (API)
Processing: One-to-one (per page)

Advantages:
- Each page processed independently
- Can parallelize with batch processing
- Better for multi-entity documents
- Faster than many-to-one for large documents
"""

from pathlib import Path
import os
from docling_graph.pipeline import run_pipeline

# Import template
from ..templates.invoice import Invoice


def main_mistral():
    """
    Extract data using Mistral API (one-to-one)
    
    Best for: Multi-page documents with one entity per page
    """
    
    print("=" * 70)
    print("EXAMPLE 7: REMOTE LLM (MISTRAL) - ONE-TO-ONE")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv("MISTRAL_API_KEY"):
        print("\nMISTRAL_API_KEY not set!")
        print("\nSetup instructions:")
        print("  1. Get API key from: https://console.mistral.ai/")
        print("  2. Set environment variable:")
        print("     export MISTRAL_API_KEY='your_key_here'")
        print("  3. Run this script again")
        return
    
    source_document = "data/multiple_invoices.pdf"
    
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        print("Please update the 'source_document' path")
        print("\nNote: This example works best with multi-page documents")
        print("      where each page contains a separate entity")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (Mistral API)")
    print("Mode: One-to-one (per page)")
    print("Model: mistral-large-latest")
    print("\nEach page will be processed separately, results merged into one graph.")
    
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
        "inference": "remote",  # Use remote API
        
        # Docling configuration
        "docling_config": "ocr",
        
        # Output configuration
        "output_dir": "outputs/example_07_remote_mistral_one_to_one",
        "export_format": "csv",
        "reverse_edges": False,
        
        # Model configuration
        "config": {
            "models": {
                "llm": {
                    "remote": {
                        "default_model": "mistral-large-latest",
                        "provider": "mistral",
                        "providers": {
                            "mistral": {
                                "default_model": "mistral-large-latest"
                            }
                        }
                    }
                }
            }
        },
        
        # Provider override
        "model_override": None,
        "provider_override": "mistral"
    }
    
    try:
        print("\n" + "-" * 70)
        print("Processing pages with Mistral API...")
        print("Each page is processed independently")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nOutputs saved to: {config['output_dir']}/")
        print("\n📊 Results:")
        print("  - Each page processed as separate invoice")
        print("  - All entities merged into one graph")
        print("  - Shared entities (same customer) automatically deduplicated")
        
        print("\n💡 Tip: For batch processing multiple documents with remote API,")
        print("   see ex05_batch_processing.py with inference='remote'")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR!")
        print("=" * 70)
        print(f"\n{type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify API key is set correctly")
        print("  2. Check API key has credits/quota")
        print("  3. Verify internet connection")
        print("  4. Check document path")
        raise


def main_openai():
    """
    Extract data using OpenAI API (one-to-one)
    """
    
    print("=" * 70)
    print("EXAMPLE 7: REMOTE LLM (OPENAI) - ONE-TO-ONE")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nOPENAI_API_KEY not set!")
        print("\nSetup instructions:")
        print("  1. Get API key from: https://platform.openai.com/api-keys")
        print("  2. Set environment variable:")
        print("     export OPENAI_API_KEY='your_key_here'")
        print("  3. Run this script again")
        return
    
    source_document = "data/multiple_invoices.pdf"
    
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (OpenAI API)")
    print("Mode: One-to-one (per page)")
    print("Model: gpt-4o")
    
    config = {
        "source": source_document,
        "template": Invoice,
        "processing_mode": "one-to-one",
        "backend_type": "llm",
        "inference": "remote",
        "docling_config": "ocr",
        "output_dir": "outputs/example_07_remote_openai_one_to_one",
        "export_format": "csv",
        "reverse_edges": False,
        "config": {
            "models": {
                "llm": {
                    "remote": {
                        "default_model": "gpt-4o",
                        "provider": "openai",
                        "providers": {
                            "openai": {
                                "default_model": "gpt-4o"
                            }
                        }
                    }
                }
            }
        },
        "model_override": None,
        "provider_override": "openai"
    }
    
    try:
        print("\n" + "-" * 70)
        print("Processing pages with OpenAI API...")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\nCompleted! Check: " + config['output_dir'] + "/")
        
    except Exception as e:
        print(f"\nError: {e}")
        raise


def main_gemini():
    """
    Extract data using Google Gemini API (one-to-one)
    """
    
    print("=" * 70)
    print("EXAMPLE 7: REMOTE LLM (GEMINI) - ONE-TO-ONE")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\nGEMINI_API_KEY not set!")
        print("\nSetup instructions:")
        print("  1. Get API key from: https://makersuite.google.com/app/apikey")
        print("  2. Set environment variable:")
        print("     export GEMINI_API_KEY='your_key_here'")
        print("  3. Run this script again")
        return
    
    source_document = "data/multiple_invoices.pdf"
    
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (Gemini API)")
    print("Mode: One-to-one (per page)")
    print("Model: gemini-2.5-flash")
    
    config = {
        "source": source_document,
        "template": Invoice,
        "processing_mode": "one-to-one",
        "backend_type": "llm",
        "inference": "remote",
        "docling_config": "ocr",
        "output_dir": "outputs/example_07_remote_gemini_one_to_one",
        "export_format": "csv",
        "reverse_edges": False,
        "config": {
            "models": {
                "llm": {
                    "remote": {
                        "default_model": "gemini-2.5-flash",
                        "provider": "gemini",
                        "providers": {
                            "gemini": {
                                "default_model": "gemini-2.5-flash"
                            }
                        }
                    }
                }
            }
        },
        "model_override": None,
        "provider_override": "gemini"
    }
    
    try:
        print("\n" + "-" * 70)
        print("Processing pages with Gemini API...")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\nCompleted! Check: " + config['output_dir'] + "/")
        
    except Exception as e:
        print(f"\nError: {e}")
        raise


def processing_mode_comparison():
    """
    When to use one-to-one vs many-to-one with remote APIs
    """
    print("\n" + "=" * 70)
    print("ONE-TO-ONE vs MANY-TO-ONE: CHOOSING THE RIGHT MODE")
    print("=" * 70)
    
    print("""
One-to-One Processing:
=====================

Use when:
--------
Multiple entities in one document (e.g., 10 invoices in one PDF)
Each page contains independent information
Pages can be processed in parallel
Need to extract separate objects per page

Example use cases:
-----------------
- Scanned invoice batches (multiple invoices per PDF)
- Contract collections
- Multi-page forms where each page is a separate submission
- Batch-scanned documents

Performance characteristics:
--------------------------
- Sequential: Processes pages one by one
- Speed: Depends on total pages (n pages = n API calls)
- Cost: Higher (more API calls)
- Accuracy: Better for independent pages

Example: 10-page PDF with 10 invoices
-------------------------------------
One-to-one:  10 API calls, ~50-100 seconds, 10 separate Invoice objects
Many-to-one: 1 API call,  ~5-10 seconds,  1 Invoice object (wrong!)


Many-to-One Processing:
=======================

Use when:
--------
Single entity spans multiple pages
Need context across all pages
Document is one cohesive unit
Want one extraction result

Example use cases:
-----------------
- Single multi-page invoice
- One contract with multiple pages
- Research papers
- Legal documents
- Reports

Performance characteristics:
--------------------------
- Single API call for entire document
- Speed: Fast (one call regardless of pages)
- Cost: Lower (one API call)
- Accuracy: Better for documents needing full context

Example: 10-page contract (one entity)
-------------------------------------
One-to-one:  10 API calls, 10 partial extractions (wrong!)
Many-to-one: 1 API call,  1 complete Contract object (correct!)


Decision Matrix:
===============

Document Type                          | Recommended Mode
-------------------------------------- | ----------------
Multiple invoices in one PDF          | ONE-TO-ONE
Single multi-page invoice             | MANY-TO-ONE
Stack of scanned receipts             | ONE-TO-ONE
One contract (multiple pages)         | MANY-TO-ONE
Batch of ID cards (one per page)      | ONE-TO-ONE
Research paper                        | MANY-TO-ONE
Multiple contracts in one file        | ONE-TO-ONE
Single long report                    | MANY-TO-ONE


Cost Comparison:
===============

10-page document with Mistral Large:

One-to-one:  10 calls × $0.004 = $0.04
Many-to-one: 1 call  × $0.008 = $0.008

➜ Many-to-one is 5x cheaper when appropriate!


Hybrid Approach:
===============

For complex workflows, combine both:

1. Split multi-entity PDFs into single-entity files
2. Use many-to-one on each file
3. Merge results

Example: 50 invoices in one PDF
-------------------------------
Step 1: Extract pages → 50 separate PDFs
Step 2: Process each with many-to-one → 50 Invoice objects
Step 3: Merge into one graph

This gives best accuracy AND reasonable cost.
""")


def batch_processing_with_remote_api():
    """
    How to efficiently batch process with remote APIs
    """
    print("\n" + "=" * 70)
    print("BATCH PROCESSING WITH REMOTE APIS")
    print("=" * 70)
    
    print("""
Remote APIs are IDEAL for batch processing because:
==================================================

1. No Local Resources Needed
   - No GPU required
   - No memory constraints
   - Consistent performance

2. High Parallelization
   - Process 10-20 documents simultaneously
   - Much faster than local models
   - Automatic load balancing

3. Scalability
   - Handle 1000s of documents
   - No infrastructure management
   - Pay only for what you use

Example Batch Configuration:
===========================

See ex05_batch_processing.py and modify for remote:

```python
from ex05_batch_processing import batch_process_documents

results = batch_process_documents(
    document_paths=[...],
    template_path="templates.Invoice",
    backend_type="llm",
    inference="remote",  # ← Change to remote
    max_workers=15,      # ← Higher parallelization
    model_name="mistral-large-latest",
    provider="mistral"
)
```

Performance Comparison:
=====================

100 documents (avg 2 pages each):

Local LLM (Ollama):
  - Workers: 4
  - Time: ~2 hours
  - Cost: $0 (but GPU needed)

Remote API (Mistral):
  - Workers: 15
  - Time: ~10 minutes
  - Cost: ~$2-5

Remote API (Gemini):
  - Workers: 20
  - Time: ~5 minutes
  - Cost: ~$0.50-2


Rate Limits:
===========

Be aware of API rate limits:

Mistral:
  - Free tier: Limited requests/minute
  - Paid tier: Higher limits

OpenAI:
  - Tier based on usage history
  - GPT-4: 10,000 TPM (tokens per minute) typical

Gemini:
  - Free tier: 60 requests/minute
  - Paid tier: Higher limits

Strategy: Adjust max_workers based on rate limits


Best Practices:
==============

1. Start with small batches
2. Monitor API usage dashboard
3. Implement exponential backoff
4. Handle rate limit errors gracefully
5. Log all API calls for debugging
6. Use cheaper models for testing
7. Cache results to avoid reprocessing
""")


if __name__ == "__main__":
    import sys
    
    print("\nRemote LLM API Examples (One-to-One)")
    print("=" * 70)
    print("\nChoose an option:")
    print("1. Mistral API (one-to-one)")
    print("2. OpenAI API (one-to-one)")
    print("3. Google Gemini API (one-to-one)")
    print("4. One-to-one vs Many-to-one comparison")
    print("5. Batch processing with remote APIs")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        main_mistral()
    elif choice == "2":
        main_openai()
    elif choice == "3":
        main_gemini()
    elif choice == "4":
        processing_mode_comparison()
    elif choice == "5":
        batch_processing_with_remote_api()
    else:
        print("Invalid choice!")
        sys.exit(1)
