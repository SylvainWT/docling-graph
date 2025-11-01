"""
Input validation functions for CLI commands.
"""

from typing import Literal

import typer
from rich import print as rich_print

from .constants import (
    BACKEND_TYPES,
    DOCLING_PIPELINES,
    EXPORT_FORMATS,
    INFERENCE_LOCATIONS,
    PROCESSING_MODES,
)


def validate_processing_mode(mode: str) -> str:
    """Validate processing mode.

    Args:
        mode: Processing mode to validate.

    Returns:
        Lowercase validated mode.

    Raises:
        typer.Exit: If mode is invalid.
    """
    mode = mode.lower()
    if mode not in PROCESSING_MODES:
        rich_print(f"[red]Error:[/red] Invalid processing mode '{mode}'.")
        rich_print(f"Must be one of: {', '.join(PROCESSING_MODES)}")
        raise typer.Exit(code=1)
    return mode


def validate_backend_type(backend: str) -> str:
    """Validate backend type.

    Args:
        backend: Backend type to validate.

    Returns:
        Lowercase validated backend.

    Raises:
        typer.Exit: If backend is invalid.
    """
    backend = backend.lower()
    if backend not in BACKEND_TYPES:
        rich_print(f"[red]Error:[/red] Invalid backend type '{backend}'.")
        rich_print(f"Must be one of: {', '.join(BACKEND_TYPES)}")
        raise typer.Exit(code=1)
    return backend


def validate_inference(inference: str) -> str:
    """Validate inference location.

    Args:
        inference: Inference location to validate.

    Returns:
        Lowercase validated inference.

    Raises:
        typer.Exit: If inference is invalid.
    """
    inference = inference.lower()
    if inference not in INFERENCE_LOCATIONS:
        rich_print(f"[red]Error:[/red] Invalid inference location '{inference}'.")
        rich_print(f"Must be one of: {', '.join(INFERENCE_LOCATIONS)}")
        raise typer.Exit(code=1)
    return inference


def validate_docling_config(config: str) -> str:
    """Validate Docling pipeline configuration.

    Args:
        config: Docling config to validate.

    Returns:
        Lowercase validated config.

    Raises:
        typer.Exit: If config is invalid.
    """
    config = config.lower()
    if config not in DOCLING_PIPELINES:
        rich_print(f"[red]Error:[/red] Invalid docling config '{config}'.")
        rich_print(f"Must be one of: {', '.join(DOCLING_PIPELINES)}")
        raise typer.Exit(code=1)
    return config


def validate_export_format(export_format: str) -> str:
    """Validate export format.

    Args:
        export_format: Export format to validate.

    Returns:
        Lowercase validated format.

    Raises:
        typer.Exit: If format is invalid.
    """
    export_format = export_format.lower()
    if export_format not in EXPORT_FORMATS:
        rich_print(f"[red]Error:[/red] Invalid export format '{export_format}'.")
        rich_print(f"Must be one of: {', '.join(EXPORT_FORMATS)}")
        raise typer.Exit(code=1)
    return export_format


def validate_vlm_constraints(backend_type: str, inference: str) -> None:
    """Validate VLM-specific constraints.

    Args:
        backend_type: Backend type.
        inference: Inference location.

    Raises:
        typer.Exit: If VLM constraints are violated.
    """
    if backend_type == "vlm" and inference == "remote":
        rich_print(
            "[red]Error:[/red] VLM (Vision-Language Model) is currently only supported with local inference."
        )
        rich_print(
            "Please use '--inference local' or switch to '--backend_type llm' for API inference."
        )
        raise typer.Exit(code=1)


def validate_provider(provider: str, inference: str) -> str:
    """Validate provider choice."""
    from .constants import API_PROVIDERS, LOCAL_PROVIDERS

    valid_providers = LOCAL_PROVIDERS if inference == "local" else API_PROVIDERS

    if provider not in valid_providers:
        raise ValueError(
            f"Invalid provider '{provider}' for inference='{inference}'. "
            f"Valid options: {', '.join(valid_providers)}"
        )
    return provider
