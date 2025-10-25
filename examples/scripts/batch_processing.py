"""
Example 5: Batch Processing with Multiprocessing
=================================================

This example demonstrates how to process multiple documents in parallel
using Python's multiprocessing for optimal performance.

Use Case:
- Processing large document collections
- Parallel extraction from multiple files
- Maximizing CPU/GPU utilization
- Production batch workflows

Requirements:
- Multiple document files to process
- Ollama running locally (or remote API configured)
- Sufficient system resources (CPU cores, RAM, GPU if using VLM)

Processing Strategy:
- Multiprocessing is used (better than threading for CPU-bound tasks)
- Each process handles one document independently
- Results can be merged into a single graph or kept separate
- Progress tracking and error handling included

Note: For VLM backend, consider GPU memory limitations when setting
      the number of parallel processes.
"""

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Optional
import time
from datetime import datetime

from docling_graph.pipeline import run_pipeline

# Import templates
from ..templates.invoice import Invoice, IDCard


def process_single_document(
    source_path: str,
    template_path: str,
    output_base_dir: str,
    backend_type: str = "llm",
    processing_mode: str = "many-to-one",
    model_name: Optional[str] = None
) -> Dict:
    """
    Process a single document and return results.
    
    This function is designed to be called by multiprocessing workers.
    
    Args:
        source_path: Path to document file
        template_path: Dotted path to Pydantic template
        output_base_dir: Base directory for outputs
        backend_type: "llm" or "vlm"
        processing_mode: "one-to-one" or "many-to-one"
        model_name: Optional model override
    
    Returns:
        Dict with processing results and metadata
    """
    start_time = time.time()
    source_file = Path(source_path)
    
    # Create unique output directory for this document
    output_dir = Path(output_base_dir) / source_file.stem
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing: {source_file.name}")
    
    # Configure pipeline
    config = {
        "source": source_path,
        "template": template_path,
        "processing_mode": processing_mode,
        "backend_type": backend_type,
        "inference": "local",
        "docling_config": "ocr" if backend_type == "llm" else "vision",
        "output_dir": str(output_dir),
        "export_format": "csv",
        "reverse_edges": False,
        "config": {
            "models": {
                "llm": {
                    "local": {
                        "default_model": model_name or "llama3:8b-instruct",
                        "provider": "ollama"
                    }
                },
                "vlm": {
                    "local": {
                        "default_model": model_name or "numind/NuExtract-2.0-8B",
                        "provider": "docling"
                    }
                }
            }
        },
        "model_override": model_name,
        "provider_override": None
    }
    
    try:
        # Run pipeline
        run_pipeline(config)
        
        elapsed = time.time() - start_time
        
        result = {
            "success": True,
            "source": source_path,
            "output_dir": str(output_dir),
            "elapsed_time": elapsed,
            "error": None
        }
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Completed: {source_file.name} ({elapsed:.2f}s)")
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        result = {
            "success": False,
            "source": source_path,
            "output_dir": str(output_dir),
            "elapsed_time": elapsed,
            "error": str(e)
        }
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed: {source_file.name} - {e}")
    
    return result


def batch_process_documents(
    document_paths: List[str],
    template_path: str,
    output_base_dir: str = "outputs/batch_processing",
    backend_type: str = "llm",
    processing_mode: str = "many-to-one",
    max_workers: Optional[int] = None,
    model_name: Optional[str] = None
) -> Dict:
    """
    Process multiple documents in parallel using multiprocessing.
    
    Args:
        document_paths: List of paths to documents
        template_path: Dotted path to Pydantic template
        output_base_dir: Base directory for all outputs
        backend_type: "llm" or "vlm"
        processing_mode: "one-to-one" or "many-to-one"
        max_workers: Number of parallel workers (None = auto)
        model_name: Optional model override
    
    Returns:
        Dict with summary of results
    """
    print("=" * 70)
    print("BATCH PROCESSING WITH MULTIPROCESSING")
    print("=" * 70)
    
    # Filter out non-existent files
    valid_paths = [p for p in document_paths if Path(p).exists()]
    invalid_paths = [p for p in document_paths if not Path(p).exists()]
    
    if invalid_paths:
        print(f"\nWarning: {len(invalid_paths)} file(s) not found:")
        for p in invalid_paths:
            print(f"  - {p}")
    
    if not valid_paths:
        print("\nNo valid documents to process!")
        return {"success": False, "results": []}
    
    print(f"\nConfiguration:")
    print(f"  Documents: {len(valid_paths)}")
    print(f"  Template: {template_path}")
    print(f"  Backend: {backend_type}")
    print(f"  Mode: {processing_mode}")
    print(f"  Workers: {max_workers or 'auto'}")
    print(f"  Model: {model_name or 'default'}")
    print(f"  Output: {output_base_dir}/")
    
    # Create output directory
    Path(output_base_dir).mkdir(parents=True, exist_ok=True)
    
    # Determine optimal number of workers
    if max_workers is None:
        import os
        max_workers = min(len(valid_paths), os.cpu_count() or 1)
    
    print(f"\nStarting {max_workers} worker(s)...")
    print("-" * 70)
    
    start_time = time.time()
    results = []
    
    # Process documents in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_path = {
            executor.submit(
                process_single_document,
                path,
                template_path,
                output_base_dir,
                backend_type,
                processing_mode,
                model_name
            ): path
            for path in valid_paths
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"\nUnexpected error processing {path}: {e}")
                results.append({
                    "success": False,
                    "source": path,
                    "output_dir": None,
                    "elapsed_time": 0,
                    "error": str(e)
                })
    
    total_time = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\nSummary:")
    print(f"  Total documents: {len(valid_paths)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average time: {total_time / len(valid_paths):.2f}s per document")
    
    if successful:
        print("\nSuccessful documents:")
        for r in successful:
            print(f"  - {Path(r['source']).name} ({r['elapsed_time']:.2f}s)")
            print(f"    Output: {r['output_dir']}")
    
    if failed:
        print("\nFailed documents:")
        for r in failed:
            print(f"  - {Path(r['source']).name}")
            print(f"    Error: {r['error']}")
    
    return {
        "success": len(failed) == 0,
        "total": len(valid_paths),
        "successful": len(successful),
        "failed": len(failed),
        "total_time": total_time,
        "results": results
    }


def example_batch_invoices():
    """
    Example: Process multiple invoice documents
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: BATCH PROCESS INVOICES")
    print("=" * 70)
    
    # List of documents to process
    documents = [
        "data/invoice_001.pdf",
        "data/invoice_002.pdf",
        "data/invoice_003.pdf",
        "data/invoice_004.pdf",
        "data/invoice_005.pdf",
    ]
    
    # Process in parallel
    results = batch_process_documents(
        document_paths=documents,
        template_path="..templates.invoice.Invoice", # For example
        output_base_dir="outputs/batch_invoices",
        backend_type="llm",
        processing_mode="many-to-one",
        max_workers=3,  # Process 3 documents at a time
        model_name="llama3:8b-instruct"
    )
    
    return results


def example_directory_processing():
    """
    Example: Process all PDFs in a directory
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: PROCESS ALL FILES IN DIRECTORY")
    print("=" * 70)
    
    # Get all PDF files from directory
    data_dir = Path("data/invoices")
    
    if not data_dir.exists():
        print(f"\nDirectory not found: {data_dir}")
        print("Create the directory and add PDF files to process")
        return
    
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\nNo PDF files found in: {data_dir}")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s) in {data_dir}")
    
    # Process all files
    results = batch_process_documents(
        document_paths=[str(f) for f in pdf_files],
        template_path="templates.Invoice",
        output_base_dir="outputs/directory_batch",
        backend_type="llm",
        processing_mode="many-to-one",
        max_workers=None,  # Auto-detect optimal number
    )
    
    return results


def performance_tips():
    """
    Tips for optimal batch processing performance
    """
    print("\n" + "=" * 70)
    print("BATCH PROCESSING PERFORMANCE TIPS")
    print("=" * 70)
    
    print("""
1. Choosing Number of Workers:
   ------------------------------
   LLM Backend (Ollama):
     - max_workers = CPU cores (or slightly less)
     - Example: 4-8 workers on 8-core CPU
   
   VLM Backend:
     - max_workers = 1 for single GPU
     - max_workers = 2-4 if you have lots of GPU memory (24GB+)
     - Processing is GPU-limited, not CPU-limited
   
   Remote API (Mistral, OpenAI):
     - max_workers = 10-20 (API rate limits apply)
     - Much faster than local processing

2. Memory Management:
   ------------------
   - Monitor RAM usage (watch free -h)
   - For VLM: Monitor GPU memory (nvidia-smi)
   - Reduce max_workers if running out of memory
   - Process in batches if dataset is very large

3. Error Handling:
   ---------------
   - Failed documents don't stop the batch
   - Check results["failed"] for errors
   - Retry failed documents separately
   - Save progress/results to JSON

4. Optimization Strategies:
   ------------------------
   - Sort documents by size (process small ones first)
   - Use faster models for initial pass
   - Pre-filter invalid/corrupted files
   - Use SSD storage for faster I/O
   - Consider cloud processing for large batches

5. Monitoring Progress:
   --------------------
   - Use logging instead of prints
   - Track timing metrics
   - Monitor system resources
   - Set up alerts for failures

6. Production Considerations:
   --------------------------
   - Add retry logic with exponential backoff
   - Implement checkpointing (save progress)
   - Use a job queue (Celery, Redis Queue)
   - Add result validation
   - Store outputs in database
""")


def main():
    """
    Main function with menu for different batch processing examples
    """
    print("\nBatch Processing Examples")
    print("=" * 70)
    print("\nChoose an example:")
    print("1. Batch process invoices (LLM)")
    print("2. Batch process contracts (VLM)")
    print("3. Process all PDFs in a directory")
    print("4. Show performance tips")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        example_batch_invoices()
    elif choice == "2":
        example_directory_processing()
    elif choice == "3":
        performance_tips()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
