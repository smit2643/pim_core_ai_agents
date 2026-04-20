from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM provider implementations."""

    @abstractmethod
    async def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> str:
        """Call the LLM and return the response text."""
