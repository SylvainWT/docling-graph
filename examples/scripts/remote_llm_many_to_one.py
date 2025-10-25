"""
Example 6: Remote LLM API with Many-to-One Processing
======================================================

This example demonstrates document extraction using remote LLM APIs
(Mistral, OpenAI, Gemini) with many-to-one processing.

Use Case:
- Fast extraction without local setup
- No GPU/compute requirements
- Production deployments with managed APIs
- Processing documents when local resources are limited

Requirements:
- API key for one of: Mistral, OpenAI, or Gemini
- Set environment variable: MISTRAL_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY
- A sample document (PDF or image)

Backend: LLM (Language Model)
Inference: Remote (API)
Processing: Many-to-one (full document)

Advantages of Remote APIs:
- Much faster than local inference
- No local GPU needed
- Consistent performance
- Better models (GPT-4, Mistral Large, etc.)
- Pay per use (no infrastructure costs)
"""

from pathlib import Path
import os
from docling_graph.pipeline import run_pipeline

# Import template
from ..templates.invoice import Invoice


def main_mistral():
    """
    Extract data using Mistral API (many-to-one)
    
    Models available:
    - mistral-large-latest (best quality)
    - mistral-small-latest (faster, cheaper)
    """
    
    print("=" * 70)
    print("EXAMPLE 6: REMOTE LLM (MISTRAL) - MANY-TO-ONE")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv("MISTRAL_API_KEY"):
        print("\nMISTRAL_API_KEY not set!")
        print("\nSetup instructions:")
        print("  1. Get API key from: https://console.mistral.ai/")
        print("  2. Set environment variable:")
        print("     export MISTRAL_API_KEY='your_key_here'")
        print("     # OR create .env file with: MISTRAL_API_KEY=your_key")
        print("  3. Run this script again")
        return
    
    source_document = "data/sample_invoice.pdf"
    
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        print("Please update the 'source_document' path")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (Mistral API)")
    print("Mode: Many-to-one (full document)")
    print("Model: mistral-large-latest")
    
    # Pipeline configuration
    config = {
        # Source document
        "source": source_document,
        
        # Template
        "template": Invoice,
        
        # Processing mode
        "processing_mode": "many-to-one",
        
        # Backend configuration
        "backend_type": "llm",
        "inference": "remote",  # Use remote API
        
        # Docling configuration
        "docling_config": "ocr",
        
        # Output configuration
        "output_dir": "outputs/example_06_remote_mistral_many_to_one",
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
        print("Calling Mistral API...")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nOutputs saved to: {config['output_dir']}/")
        print("\nAdvantages of remote API:")
        print("  Much faster than local inference")
        print("  No GPU required")
        print("  Consistent performance")
        print("  Access to best models")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR!")
        print("=" * 70)
        print(f"\n{type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify API key is set correctly")
        print("  2. Check API key has credits/quota")
        print("  3. Verify internet connection")
        print("  4. Check Mistral API status")
        raise


def main_openai():
    """
    Extract data using OpenAI API (many-to-one)
    
    Models available:
    - gpt-4o (best quality, vision capable)
    - gpt-4o-mini (faster, cheaper)
    - gpt-4-turbo
    """
    
    print("=" * 70)
    print("EXAMPLE 6: REMOTE LLM (OPENAI) - MANY-TO-ONE")
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
    
    source_document = "data/sample_invoice.pdf"
    
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (OpenAI API)")
    print("Mode: Many-to-one (full document)")
    print("Model: gpt-4o")
    
    config = {
        "source": source_document,
        "template": Invoice,
        "processing_mode": "many-to-one",
        "backend_type": "llm",
        "inference": "remote",
        "docling_config": "ocr",
        "output_dir": "outputs/example_06_remote_openai_many_to_one",
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
        print("Calling OpenAI API...")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\nCompleted! Check: " + config['output_dir'] + "/")
        
    except Exception as e:
        print(f"\nError: {e}")
        raise


def main_gemini():
    """
    Extract data using Google Gemini API (many-to-one)
    
    Models available:
    - gemini-2.5-flash (fast, good quality)
    - gemini-pro
    """
    
    print("=" * 70)
    print("EXAMPLE 6: REMOTE LLM (GEMINI) - MANY-TO-ONE")
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
    
    source_document = "data/sample_invoice.pdf"
    
    if not Path(source_document).exists():
        print(f"\nDocument not found: {source_document}")
        return
    
    print(f"\nProcessing: {source_document}")
    print("Template: Invoice")
    print("Backend: LLM (Gemini API)")
    print("Mode: Many-to-one (full document)")
    print("Model: gemini-2.5-flash")
    
    config = {
        "source": source_document,
        "template": Invoice,
        "processing_mode": "many-to-one",
        "backend_type": "llm",
        "inference": "remote",
        "docling_config": "ocr",
        "output_dir": "outputs/example_06_remote_gemini_many_to_one",
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
        print("Calling Gemini API...")
        print("-" * 70 + "\n")
        
        run_pipeline(config)
        
        print("\nCompleted! Check: " + config['output_dir'] + "/")
        
    except Exception as e:
        print(f"\nError: {e}")
        raise


def compare_providers():
    """
    Comparison of different API providers
    """
    print("\n" + "=" * 70)
    print("API PROVIDER COMPARISON")
    print("=" * 70)
    
    print("""
Provider Comparison:
===================

Mistral AI:
----------
Models: mistral-large-latest, mistral-small-latest
Pros: European provider, good for French/EU documents, competitive pricing
Cons: Smaller model selection than OpenAI
Best for: French documents, EU data compliance
Pricing: ~€0.002-0.008 per 1K tokens

OpenAI:
-------
Models: gpt-4o, gpt-4o-mini, gpt-4-turbo
Pros: Best overall quality, largest model selection, vision capable
Cons: More expensive than alternatives
Best for: Highest accuracy requirements, complex documents
Pricing: ~$0.005-0.03 per 1K tokens

Google Gemini:
-------------
Models: gemini-2.5-flash, gemini-pro
Pros: Fast, competitive pricing, good context window
Cons: Newer, less established than OpenAI
Best for: Fast processing, good balance of cost/quality
Pricing: ~$0.0001-0.002 per 1K tokens

Recommendation:
--------------
1. Start with Mistral (good balance, EU-friendly)
2. Use OpenAI for maximum accuracy
3. Use Gemini for high-volume/cost-sensitive workloads
4. Test all three and compare results for your specific use case

Speed Comparison (approximate):
------------------------------
Gemini Flash:     ~2-5 seconds per document
Mistral Small:    ~3-8 seconds per document
OpenAI GPT-4o:    ~5-10 seconds per document
Mistral Large:    ~5-12 seconds per document

(vs Local LLM:    ~30-120 seconds per document)
""")


def cost_estimation():
    """
    Estimate API costs for batch processing
    """
    print("\n" + "=" * 70)
    print("API COST ESTIMATION")
    print("=" * 70)
    
    print("""
Typical Document Processing Costs:
==================================

Assumptions:
- Average document: 2 pages, ~1000 tokens
- Extraction: ~500 tokens output
- Total: ~1500 tokens per document

Cost per 100 documents:
----------------------
Mistral Small:   ~$0.30 - $0.80
Gemini Flash:    ~$0.01 - $0.30
OpenAI GPT-4o:   ~$1.00 - $4.50
Mistral Large:   ~$1.20 - $2.40

Cost per 1000 documents:
-----------------------
Mistral Small:   ~$3 - $8
Gemini Flash:    ~$0.10 - $3
OpenAI GPT-4o:   ~$10 - $45
Mistral Large:   ~$12 - $24

Tips to Reduce Costs:
--------------------
1. Use smaller models when possible
2. Optimize prompts to reduce token usage
3. Cache common extractions
4. Batch process during off-peak hours
5. Use local models for development/testing
6. Monitor usage with API dashboards

When to Use Remote vs Local:
---------------------------
Remote API if:
  - Processing < 1000 docs/month
  - Need fast results
  - No GPU available
  - Prototyping/development

Local Model if:
  - Processing > 10,000 docs/month
  - Have GPU infrastructure
  - Data privacy requirements
  - Long-term production use
""")


if __name__ == "__main__":
    import sys
    
    print("\nRemote LLM API Examples (Many-to-One)")
    print("=" * 70)
    print("\nChoose a provider:")
    print("1. Mistral AI (recommended for EU)")
    print("2. OpenAI (highest accuracy)")
    print("3. Google Gemini (fastest/cheapest)")
    print("4. Compare providers")
    print("5. Cost estimation guide")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        main_mistral()
    elif choice == "2":
        main_openai()
    elif choice == "3":
        main_gemini()
    elif choice == "4":
        compare_providers()
    elif choice == "5":
        cost_estimation()
    else:
        print("Invalid choice!")
        sys.exit(1)
