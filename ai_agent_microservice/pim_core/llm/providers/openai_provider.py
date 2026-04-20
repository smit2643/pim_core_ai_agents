from __future__ import annotations

from pim_core.llm.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider. Supports gpt-*, o1-*, o3-*, o4-* model names."""

    def __init__(self) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package is required to use OpenAI models. "
                "Install it with: pip install openai"
            ) from exc

        from pim_core.config import settings
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Add it to your .env file to use OpenAI models."
            )

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> str:
        all_messages = [{"role": "system", "content": system}] + messages
        response = await self._client.chat.completions.create(
            model=model,
            messages=all_messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
