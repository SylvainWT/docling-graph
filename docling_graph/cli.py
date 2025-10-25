import typer
from typing_extensions import Annotated
from pathlib import Path
from rich import print
import sys
import yaml
import click

sys.path.append(str(Path.cwd()))

from .pipeline import run_pipeline

app = typer.Typer(
    name="docling-graph",
    help="A tool to convert documents into knowledge graphs using configurable pipelines.",
    add_completion=False
)

CONFIG_FILE_NAME = "config.yaml"

@app.command(
    name="init",
    help=f"Create a default {CONFIG_FILE_NAME} in the current directory with interactive setup."
)
def init_command():
    """Creates a customized configuration file through interactive prompts."""
    from shutil import copy
    
    output_path = Path.cwd() / CONFIG_FILE_NAME
    
    # Check if config already exists
    if output_path.exists():
        print(f"[yellow]'{CONFIG_FILE_NAME}' already exists in this directory.[/yellow]")
        overwrite = typer.confirm("Do you want to overwrite it?")
        if not overwrite:
            print("Initialization cancelled.")
            raise typer.Abort()
    
    print("[bold blue]Welcome to Docling-Graph Setup![/bold blue]")
    print("Let's configure your knowledge graph pipeline.\n")
    
    # ===== DEFAULTS SECTION =====
    print("[bold cyan]── Default Settings ──[/bold cyan]")
    
    # Processing Mode
    print("\n[bold]1. Processing Mode[/bold]")
    print("  [dim]How should documents be processed?[/dim]")
    print("  • [cyan]one-to-one[/cyan]: Process each page individually (better for multi-page docs with distinct sections)")
    print("  • [cyan]many-to-one[/cyan]: Process entire document as one unit (better for cohesive documents)")
    processing_mode = typer.prompt(
        "Select processing mode",
        type=click.Choice(["one-to-one", "many-to-one"], case_sensitive=False),
        default="one-to-one"
    )
    
    # Backend Type
    print("\n[bold]2. Backend Type[/bold]")
    print("  [dim]Which AI backend should be used for extraction?[/dim]")
    print("  • [cyan]llm[/cyan]: Language Model (text-based, works with OCR output)")
    print("  • [cyan]vlm[/cyan]: Vision-Language Model (processes document images directly)")
    backend_type = typer.prompt(
        "Select backend type",
        type=click.Choice(["llm", "vlm"], case_sensitive=False),
        default="llm"
    )
    
    # Inference Location
    print("\n[bold]3. Inference Location[/bold]")
    print("  [dim]Where should the model run?[/dim]")
    
    if backend_type == "vlm":
        print("  [yellow]Note: VLM currently only supports local inference[/yellow]")
        inference = "local"
    else:
        print("  • [cyan]local[/cyan]: Run models on your machine (requires Ollama or local models)")
        print("  • [cyan]remote[/cyan]: Use cloud APIs (requires API keys)")
        inference = typer.prompt(
            "Select inference location",
            type=click.Choice(["local", "remote"], case_sensitive=False),
            default="remote"
        )
    
    # Export Format
    print("\n[bold]4. Export Format[/bold]")
    print("  [dim]How should the knowledge graph be exported?[/dim]")
    print("  • [cyan]csv[/cyan]: CSV files (nodes.csv, edges.csv) - easy to import into Neo4j or analyze")
    print("  • [cyan]cypher[/cyan]: Cypher query language - direct Neo4j import script")
    export_format = typer.prompt(
        "Select export format",
        type=click.Choice(["csv", "cypher"], case_sensitive=False),
        default="csv"
    )
    
    # ===== DOCLING PIPELINE SECTION =====
    print("\n[bold cyan]── Docling Pipeline Configuration ──[/bold cyan]")
    print("\n[bold]5. Document Processing Pipeline[/bold]")
    print("  [dim]Which pipeline should Docling use for document conversion?[/dim]")
    print("  • [cyan]ocr[/cyan]: OCR pipeline (most accurate for standard documents)")
    print("  • [cyan]vision[/cyan]: Vision-Language Model pipeline (best for complex layouts)")
    docling_pipeline = typer.prompt(
        "Select docling pipeline",
        type=click.Choice(["ocr", "vision"], case_sensitive=False),
        default="ocr"
    )
    
    # ===== MODEL CONFIGURATION SECTION =====
    print("\n[bold cyan]── Model Configuration ──[/bold cyan]")
    
    # Configure based on backend and inference choices
    if backend_type == "vlm":
        print("\n[bold]6. VLM Local Model[/bold]")
        print("  [dim]Vision-Language Model for local inference[/dim]")
        print("  • [cyan]numind/NuExtract-2.0-8B[/cyan]: Default (balanced performance)")
        print("  • [cyan]numind/NuExtract-2.0-2B[/cyan]: Faster, less accurate")
        print("  • [cyan]custom[/cyan]: Enter your own model")
        vlm_choice = typer.prompt(
            "Select VLM model",
            type=str,
            default="numind/NuExtract-2.0-8B"
        )
        vlm_model = vlm_choice if vlm_choice != "custom" else typer.prompt("Enter custom model path")
        llm_local_model = "llama3:8b-instruct"  # Default for potential use
        llm_remote_model = "mistral-small-latest"
        llm_remote_provider = "mistral"
    else:  # llm backend
        if inference == "local":
            print("\n[bold]6. LLM Local Model[/bold]")
            print("  [dim]Language Model for local inference (requires Ollama)[/dim]")
            print("  • [cyan]llama3:8b-instruct[/cyan]: Default Llama 3 model")
            print("  • [cyan]llama3:70b-instruct[/cyan]: Larger, more capable")
            print("  • [cyan]mistral:7b-instruct[/cyan]: Mistral model")
            print("  • [cyan]custom[/cyan]: Enter your own Ollama model")
            llm_choice = typer.prompt(
                "Select LLM model",
                type=str,
                default="llama3:8b-instruct"
            )
            llm_local_model = llm_choice if llm_choice != "custom" else typer.prompt("Enter Ollama model name")
            llm_remote_model = "mistral-small-latest"
            llm_remote_provider = "mistral"
            vlm_model = "numind/NuExtract-2.0-8B"  # Default for potential use
        else:  # remote
            print("\n[bold]6. API Provider[/bold]")
            print("  [dim]Which API provider do you want to use?[/dim]")
            print("  • [cyan]mistral[/cyan]: Mistral AI")
            print("  • [cyan]openai[/cyan]: OpenAI (GPT models)")
            print("  • [cyan]gemini[/cyan]: Google Gemini")
            llm_remote_provider = typer.prompt(
                "Select API provider",
                type=click.Choice(["mistral", "openai", "gemini"], case_sensitive=False),
                default="mistral"
            )
            
            # Set default models based on provider
            provider_defaults = {
                "mistral": "mistral-small-latest",
                "openai": "gpt-4-turbo",
                "gemini": "gemini-2.5-flash"
            }
            llm_remote_model = typer.prompt(
                f"Model name for {llm_remote_provider}",
                type=str,
                default=provider_defaults[llm_remote_provider]
            )
            llm_local_model = "llama3:8b-instruct"  # Default for potential use
            vlm_model = "numind/NuExtract-2.0-8B"  # Default for potential use
    
    # ===== OUTPUT SETTINGS SECTION =====
    print("\n[bold cyan]── Output Settings ──[/bold cyan]")
    
    print("\n[bold]7. Output Directory[/bold]")
    output_directory = typer.prompt(
        "Default output directory",
        type=str,
        default="outputs"
    )
    
    print("\n[bold]8. Visualization Options[/bold]")
    create_visualizations = typer.confirm(
        "Create interactive graph visualizations?",
        default=True
    )
    
    create_markdown = typer.confirm(
        "Create markdown documentation?",
        default=True
    )
    
    # ===== BUILD CONFIG DICTIONARY =====
    config_dict = {
        "defaults": {
            "processing_mode": processing_mode,
            "backend_type": backend_type,
            "inference": inference,
            "export_format": export_format
        },
        "docling": {
            "pipeline": docling_pipeline
        },
        "models": {
            "vlm": {
                "local": {
                    "default_model": vlm_model,
                    "provider": "docling"
                }
            },
            "llm": {
                "local": {
                    "default_model": llm_local_model,
                    "provider": "ollama"
                },
                "remote": {
                    "default_model": llm_remote_model,
                    "provider": llm_remote_provider
                },
                "providers": {
                    "mistral": {
                        "default_model": "mistral-small-latest"
                    },
                    "openai": {
                        "default_model": "gpt-4-turbo"
                    },
                    "gemini": {
                        "default_model": "gemini-2.5-flash"
                    }
                }
            }
        },
        "output": {
            "default_directory": output_directory,
            "create_visualizations": create_visualizations,
            "create_markdown": create_markdown
        }
    }
    
    # Update the remote model in providers section
    config_dict["models"]["llm"]["providers"][llm_remote_provider]["default_model"] = llm_remote_model
    
    # ===== WRITE CONFIG FILE =====
    try:
        with open(output_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print(f"\n[green]Successfully created '{output_path}'[/green]")
        print("\n[bold]Next steps:[/bold]")
        
        if inference == "local" and backend_type == "llm":
            print(f"  1. Make sure Ollama is running: [cyan]ollama serve[/cyan]")
            print(f"  2. Pull the model: [cyan]ollama pull {llm_local_model}[/cyan]")
            print(f"  3. Run a conversion: [cyan]docling-graph convert document.pdf -t templates.invoice.Invoice[/cyan]")
        elif inference == "remote":
            print(f"  1. Set your API key: [cyan]export {llm_remote_provider.upper()}_API_KEY='your_key'[/cyan]")
            print(f"  2. Run a conversion: [cyan]docling-graph convert document.pdf -t templates.invoice.Invoice[/cyan]")
        else:  # VLM local
            print(f"  1. Ensure VLM model is available locally")
            print(f"  2. Run a conversion: [cyan]docling-graph convert document.pdf -t templates.invoice.Invoice[/cyan]")
        
        print(f"\n[dim]You can edit '{CONFIG_FILE_NAME}' anytime to adjust your configuration.[/dim]")
        
    except Exception as e:
        print(f"[red]Error creating config file:[/red] {e}")
        raise typer.Exit(code=1)


def _load_config() -> dict:
    """Loads the config file from the current directory."""
    config_path = Path.cwd() / CONFIG_FILE_NAME
    
    if not config_path.exists():
        print(f"[red]Error:[/red] Configuration file '{CONFIG_FILE_NAME}' not found.")
        print(f"Please run [cyan]docling-graph init[/cyan] first.")
        raise typer.Exit(code=1)
    
    with open(config_path, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"[red]Error parsing '{CONFIG_FILE_NAME}':[/red] {e}")
            raise typer.Exit(code=1)


@app.command(
    name="convert",
    help="Convert a document to a knowledge graph."
)
def convert_command(
    source: Annotated[Path, typer.Argument(
        help="Path to the source document (PDF, JPG, PNG).",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    )],
    template: Annotated[str, typer.Option(
        "--template", "-t",
        help="Dotted path to the Pydantic template class (e.g., 'templates.invoice.Invoice')."
    )],
    
    # --- Three Independent Configuration Dimensions ---
    processing_mode: Annotated[str, typer.Option(
        "--processing-mode", "-p",
        help="Processing strategy: 'one-to-one' (per page) or 'many-to-one' (entire document)."
    )] = "many-to-one",
    
    backend_type: Annotated[str, typer.Option(
        "--backend_type", "-b",
        help="Backend type: 'llm' (Language Model) or 'vlm' (Vision-Language Model)."
    )] = "vlm",
    
    inference: Annotated[str, typer.Option(
        "--inference", "-i",
        help="Inference location: 'local' or 'remote'."
    )] = "local",
    
    docling_config: Annotated[str, typer.Option(
        "--docling-config", "-d",
        help="Docling pipeline configuration: 'ocr' or 'vision' (Vision-Language Model)."
    )] = None,
    
    # --- Optional Overrides ---
    output_dir: Annotated[Path, typer.Option(
        "--output-dir", "-o",
        help="Directory to save the output files.",
        file_okay=False,
        writable=True
    )] = Path("outputs"),
    
    model: Annotated[str, typer.Option(
        "--model",
        help="Override specific model name (e.g., 'mistral-large-latest', 'llama3:8b')."
    )] = None,
    
    provider: Annotated[str, typer.Option(
        "--provider",
        help="Override provider (e.g., 'mistral', 'openai', 'ollama')."
    )] = None,
    
    export_format: Annotated[str, typer.Option(
        "--export-format", "-e",
        help="Format to export the graph data (csv or cypher)."
    )] = "csv",
    
    reverse_edges: Annotated[bool, typer.Option(
        "--reverse-edges", "-r",
        help="Create bidirectional edges in the knowledge graph for easier querying."
    )] = False
):
    """
    Main CLI command to convert a document to a knowledge graph.
    """
    print("--- [blue]Initiating Docling-Graph Conversion[/blue] ---")
    
    # Load config
    config_data = _load_config()
    
    # Update the config loading section
    defaults = config_data.get('defaults', {})
    
    # Use CLI values if provided, otherwise fall back to config defaults
    processing_mode = (processing_mode or defaults.get('processing_mode', 'many-to-one')).lower()
    backend_type = (backend_type or defaults.get('backend_type', 'llm')).lower()
    inference = (inference or defaults.get('inference', 'local')).lower()
    export_format = (export_format or defaults.get('export_format', 'csv')).lower()
    docling_config = (docling_config or config_data.get('docling', {}).get('pipeline', 'ocr')).lower()
    
    # Arguments validation
    if processing_mode not in ["one-to-one", "many-to-one"]:
        print(f"[red]Error:[/red] Invalid processing mode '{processing_mode}'. Must be 'one-to-one' or 'many-to-one'.")
        raise typer.Exit(code=1)
    
    if backend_type not in ["llm", "vlm"]:
        print(f"[red]Error:[/red] Invalid backend type '{backend_type}'. Must be 'llm' or 'vlm'.")
        raise typer.Exit(code=1)
    
    if inference not in ["local", "remote"]:
        print(f"[red]Error:[/red] Invalid inference location '{inference}'. Must be 'local' or 'remote'.")
        raise typer.Exit(code=1)
    
    if docling_config not in ["ocr", "vision"]:
        print(f"[red]Error:[/red] Invalid docling config '{docling_config}'. Must be 'ocr' or 'vision'.")
        raise typer.Exit(code=1)
    
    if export_format not in ["csv", "cypher"]:
        print(f"[red]Error:[/red] Invalid export format '{export_format}'. Must be 'csv' or 'cypher'.")
        raise typer.Exit(code=1)
    
    # Validate VLM constraint (VLM only works locally for now)
    if backend_type == "vlm" and inference == "remote":
        print(f"[red]Error:[/red] VLM (Vision-Language Model) is currently only supported with local inference.")
        print("Please use '--inference local' or switch to '--backend_type llm' for API inference.")
        raise typer.Exit(code=1)
    
    # Display configuration
    print(f"Configuration:")
    print(f"  Docling config: [cyan]{docling_config}[/cyan]")
    print(f"  Processing mode: [cyan]{processing_mode}[/cyan]")
    print(f"  Backend type: [cyan]{backend_type}[/cyan]")
    print(f"  Inference: [cyan]{inference}[/cyan]")
    print(f"  Reverse edges: [cyan]{str(reverse_edges).lower()}[/cyan]")
    print(f"  Export format: [cyan]{export_format}[/cyan]")
    
    # Bundle settings for the pipeline
    run_config = {
        "source": str(source),
        "template": template,
        "output_dir": str(output_dir),
        "docling_config": docling_config,
        "processing_mode": processing_mode,
        "backend_type": backend_type,
        "inference": inference,
        "reverse_edges": reverse_edges,
        "export_format": export_format,
        "config": config_data,
        "model_override": model,
        "provider_override": provider
    }
    
    try:
        run_pipeline(run_config)
    except Exception as e:
        print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


def main():
    app()