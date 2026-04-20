from __future__ import annotations

from pim_core.llm.factory import get_provider


class LLMClient:
    """Provider-agnostic async LLM client.

    Delegates to the appropriate provider based on the model name.
    Defaults to settings.claude_model when no model is specified.
    """

    async def complete(
        self,
        system: str,
        messages: list[dict],
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        """Call the LLM and return the response text."""
        from pim_core.config import settings
        model_name = model or settings.claude_model
        provider = get_provider(model_name)
        return await provider.complete(
            model=model_name,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
        )


llm_client = LLMClient()
