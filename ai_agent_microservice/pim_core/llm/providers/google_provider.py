from __future__ import annotations

from pim_core.llm.providers.base import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider. Supports gemini-* model names."""

    def __init__(self) -> None:
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "google-generativeai package is required to use Gemini models. "
                "Install it with: pip install google-generativeai"
            ) from exc

        from pim_core.config import settings
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Add it to your .env file to use Gemini models."
            )

        genai.configure(api_key=settings.google_api_key)
        self._genai = genai

    async def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> str:
        client = self._genai.GenerativeModel(
            model_name=model,
            system_instruction=system,
        )
        gemini_messages = [
            {
                "role": "user" if m["role"] == "user" else "model",
                "parts": [m["content"]],
            }
            for m in messages
        ]
        response = await client.generate_content_async(
            gemini_messages,
            generation_config=self._genai.GenerationConfig(
                max_output_tokens=max_tokens,
            ),
        )
        return response.text
