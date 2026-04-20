from __future__ import annotations

from pim_core.llm.providers.base import BaseLLMProvider

_instances: dict[str, BaseLLMProvider] = {}

_OPENAI_PREFIXES = ("gpt-", "o1-", "o3-", "o4-")


def get_provider(model_name: str) -> BaseLLMProvider:
    """Return the cached provider instance for the given model name.

    Provider is determined by model name prefix:
    - claude-*                   → AnthropicProvider
    - gpt-*, o1-*, o3-*, o4-*   → OpenAIProvider
    - gemini-*                   → GoogleProvider

    Raises:
        ValueError: When no provider is registered for the model prefix.
    """
    if model_name.startswith("claude-"):
        key = "anthropic"
        if key not in _instances:
            from pim_core.llm.providers.anthropic_provider import AnthropicProvider
            _instances[key] = AnthropicProvider()
        return _instances[key]

    if model_name.startswith(_OPENAI_PREFIXES):
        key = "openai"
        if key not in _instances:
            from pim_core.llm.providers.openai_provider import OpenAIProvider
            _instances[key] = OpenAIProvider()
        return _instances[key]

    if model_name.startswith("gemini-"):
        key = "google"
        if key not in _instances:
            from pim_core.llm.providers.google_provider import GoogleProvider
            _instances[key] = GoogleProvider()
        return _instances[key]

    raise ValueError(
        f"No provider found for model '{model_name}'. "
        f"Supported prefixes: claude-, gpt-, o1-, o3-, o4-, gemini-"
    )
