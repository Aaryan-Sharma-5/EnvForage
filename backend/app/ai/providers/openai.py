from typing import Any

import httpx
from backend.app.ai.providers.base import LLMProvider
from backend.app.core.exceptions import LLMProviderError


class OpenAIProvider(LLMProvider):
    """Direct provider implementation for enterprise OpenAI API integration."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        if not api_key:
            raise LLMProviderError("OpenAI API key configuration is missing.")
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_response(self, model: str, messages: list, temperature: float = 0.2) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model or "gpt-4o",
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise LLMProviderError(f"OpenAI API error occurred: {e.response.text}")
            except Exception as e:
                raise LLMProviderError(f"Unexpected connection error under OpenAI provider: {str(e)}")
