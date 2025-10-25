import json
import os

from typing import Dict, Any
from openai import OpenAI

from .base import BaseLlmClient
from dotenv import load_dotenv
from rich import print


# Load environment variables from .env file
load_dotenv()

class OpenAIClient(BaseLlmClient):
    """OpenAI API implementation of the LLM Client."""

    def __init__(self, model: str):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("[OpenAIClient] [red]Error:[/red] OPENAI_API_KEY not set.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # --- Context Limits ---
        model_context_limits = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 16000
        }
        
        self._context_limit = model_context_limits.get(model, 128000)
        print(f"[OpenAIClient] Initialized for [blue]{self.model}[/blue]")

    def get_json_response(self, prompt: str, schema_json: str) -> Dict[str, Any]:
        """Executes the OpenAI chat completion call with JSON mode."""
        
        # Use chat completions with JSON mode
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that responds in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract the JSON content from the response
        content = response.choices[0].message.content
        return json.loads(content)

    @property
    def context_limit(self) -> int:
        return self._context_limit
