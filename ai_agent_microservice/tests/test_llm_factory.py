import pytest
from unittest.mock import patch, MagicMock


def test_get_provider_returns_anthropic_for_claude_model():
    """claude-* model prefix routes to AnthropicProvider."""
    from pim_core.llm.factory import _instances
    _instances.clear()

    with patch("anthropic.AsyncAnthropic"):
        from pim_core.llm.factory import get_provider
        from pim_core.llm.providers.anthropic_provider import AnthropicProvider
        provider = get_provider("claude-sonnet-4-6")

    assert isinstance(provider, AnthropicProvider)


def test_get_provider_returns_openai_for_gpt_model():
    """gpt-* model prefix routes to OpenAIProvider."""
    from pim_core.llm.factory import _instances
    _instances.clear()

    from pim_core.llm.providers.openai_provider import OpenAIProvider
    # Patch __init__ so we test routing only — no real API key or package needed.
    with patch.object(OpenAIProvider, "__init__", return_value=None):
        from pim_core.llm.factory import get_provider
        provider = get_provider("gpt-4o")

    assert isinstance(provider, OpenAIProvider)


def test_get_provider_returns_google_for_gemini_model():
    """gemini-* model prefix routes to GoogleProvider."""
    from pim_core.llm.factory import _instances
    _instances.clear()

    from pim_core.llm.providers.google_provider import GoogleProvider
    # Patch __init__ so we test routing only — no real API key or package needed.
    with patch.object(GoogleProvider, "__init__", return_value=None):
        from pim_core.llm.factory import get_provider
        provider = get_provider("gemini-1.5-pro")

    assert isinstance(provider, GoogleProvider)


def test_get_provider_caches_instance():
    """Calling get_provider twice with same prefix returns the same instance."""
    from pim_core.llm.factory import _instances
    _instances.clear()

    with patch("anthropic.AsyncAnthropic"):
        from pim_core.llm.factory import get_provider
        p1 = get_provider("claude-sonnet-4-6")
        p2 = get_provider("claude-opus-4-6")

    assert p1 is p2


def test_get_provider_raises_for_unknown_prefix():
    """Unrecognised model prefix raises ValueError with helpful message."""
    from pim_core.llm.factory import get_provider
    with pytest.raises(ValueError, match="No provider found"):
        get_provider("llama3-70b")
