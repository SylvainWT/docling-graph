"""
Mistral API client implementation.

Based on https://docs.mistral.ai/api/endpoint/chat
"""

import json
import os
from typing import Any, Dict, cast

from dotenv import load_dotenv
from rich import print as rich_print

from .llm_base import BaseLlmClient

# Load environment variables
load_dotenv()

# Requires `pip install mistralai`
# Make the lazy import optional to satisfy type checkers when assigning None
_Mistral: Any | None = None
try:
    from mistralai import Mistral as Mistral_module

    _Mistral = Mistral_module
except ImportError:
    rich_print(
        "[red]Error:[/red] `mistralai` package not found. "
        "Please run `pip install mistralai` to use Mistral client."
    )
    _Mistral = None

# Expose as Any to allow None fallback without mypy issues
Mistral: Any = _Mistral


class MistralClient(BaseLlmClient):
    """Mistral API implementation matching official example."""

    def __init__(self, model: str) -> None:
        self.model = model
        self.api_key = os.getenv("MISTRAL_API_KEY")

        if not self.api_key:
            raise ValueError(
                "[MistralClient] [red]Error:[/red] MISTRAL_API_KEY not set. "
                "Please set it in your environment or .env file."
            )

        # Initialize Mistral client
        self.client = Mistral(api_key=self.api_key)

        # Context limits for different models
        model_context_limits = {
            "mistral-large-latest": 128000,
            "mistral-medium-latest": 128000,
            "mistral-small-latest": 32000,
        }

        self._context_limit = model_context_limits.get(model, 32000)
        rich_print(f"[MistralClient] Initialized for [blue]{self.model}[/blue]")

    def get_json_response(self, prompt: str | dict, schema_json: str) -> Dict[str, Any]:
        """
        Execute Mistral chat.complete with proper message structure.

        Official example: https://docs.mistral.ai/api/endpoint/chat

        Args:
            prompt: Either a string (legacy) or dict with 'system' and 'user' keys.
            schema_json: JSON schema (for reference).

        Returns:
            Parsed JSON response from Mistral.
        """
        # Build messages list - EXACTLY like official example
        messages: list[dict[str, str]] = []

        if isinstance(prompt, dict):
            # Extract system and user content
            system_content = prompt.get("system", "")
            user_content = prompt.get("user", "")

            # Validate we have content
            if not system_content or not user_content:
                rich_print("[yellow]Warning:[/yellow] Empty system or user prompt")
                rich_print(f"  System: {bool(system_content)}")
                rich_print(f"  User: {bool(user_content)}")

            # Add system message if present
            if system_content:
                messages.append(
                    {
                        "role": "system",
                        "content": system_content,
                    }
                )

            # Add user message
            messages.append(
                {
                    "role": "user",
                    "content": user_content or "Please provide a JSON response.",
                }
            )
        else:
            # Legacy string prompt
            if not prompt:
                rich_print("[yellow]Warning:[/yellow] Empty prompt string")
                prompt = "Please provide a JSON response."

            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

        try:
            # Call Mistral API
            # The SDK expects typed message objects; cast our dict list for type-checking
            res = self.client.chat.complete(
                model=self.model,
                messages=cast(Any, messages),
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            # Get response content
            response_content = res.choices[0].message.content

            # Parse JSON
            if not response_content:
                rich_print("[red]Error:[/red] Mistral returned empty content")
                return {}

            try:
                # response_content may be str or list of chunks; handle both
                if isinstance(response_content, str):
                    raw = response_content
                else:
                    # Extract text from any chunk-like objects
                    parts: list[str] = []
                    for chunk in response_content:
                        text = getattr(chunk, "text", None)
                        if isinstance(text, str):
                            parts.append(text)
                    raw = "".join(parts)

                parsed = json.loads(raw)

                # Validate it's not empty
                if not parsed or (isinstance(parsed, dict) and not any(parsed.values())):
                    rich_print("[yellow]Warning:[/yellow] Mistral returned empty or all-null JSON")

                # Ensure return type is a dict
                if isinstance(parsed, dict):
                    return cast(Dict[str, Any], parsed)
                else:
                    rich_print(
                        "[yellow]Warning:[/yellow] Expected a JSON object; got non-dict. Returning empty dict."
                    )
                    return {}

            except json.JSONDecodeError as e:
                rich_print(f"[red]Error:[/red] Failed to parse Mistral response as JSON: {e}")
                rich_print(f"[yellow]Raw response:[/yellow] {response_content}")
                return {}

        except Exception as e:
            rich_print(f"[red]Error:[/red] Mistral API call failed: {e}")
            import traceback

            traceback.print_exc()
            return {}

    @property
    def context_limit(self) -> int:
        return self._context_limit
