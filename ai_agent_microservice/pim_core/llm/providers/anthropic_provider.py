from __future__ import annotations

import anthropic

from pim_core.config import settings
from pim_core.llm.providers.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider. Supports all claude-* model names."""

    def __init__(self) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> str:
        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text
