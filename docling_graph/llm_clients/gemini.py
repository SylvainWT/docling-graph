import json
import os

from typing import Dict, Any
from google import genai

from .llm_base import BaseLlmClient
from dotenv import load_dotenv
from rich import print

# Load environment variables from .env file
load_dotenv()


class GeminiClient(BaseLlmClient):
    """Google Gemini API implementation of the LLM Client."""

    def __init__(self, model: str):
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("[GeminiClient] [red]Error:[/red] GEMINI_API_KEY not set.")
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        # --- Context Limits ---
        model_context_limits = {
            "gemini-1.5-flash": 32000,
            "gemini-1.5-pro": 128000,
            "gemini-2.5-flash": 128000,
            "gemini-2.5-pro": 1000000
        }
        
        self._context_limit = model_context_limits.get(model, 100000)
        print(f"[GeminiClient] Initialized for [blue]{self.model}[/blue]")

    def get_json_response(self, prompt: str, schema_json: str) -> Dict[str, Any]:
        """Executes the Gemini generate_content call."""
        
        # Configure JSON response mode
        generation_config = {
            "response_mime_type": "application/json",
        }
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=generation_config
        )
        
        return json.loads(response.text)

    @property
    def context_limit(self) -> int:
        return self._context_limit
