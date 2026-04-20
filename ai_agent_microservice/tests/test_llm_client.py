import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_llm_client_complete_returns_text():
    """LLMClient.complete returns the text from the provider."""
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value="Generated product description.")

    with patch("pim_core.llm.client.get_provider", return_value=mock_provider):
        from pim_core.llm.client import LLMClient
        client = LLMClient()
        result = await client.complete(
            system="You are a copywriter.",
            messages=[{"role": "user", "content": "Write a title."}],
            model="claude-sonnet-4-6",
        )

    assert result == "Generated product description."


@pytest.mark.asyncio
async def test_llm_client_passes_model_to_provider():
    """LLMClient.complete forwards the model name to the provider."""
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value="ok")

    with patch("pim_core.llm.client.get_provider", return_value=mock_provider):
        from pim_core.llm.client import LLMClient
        client = LLMClient()
        await client.complete(
            system="sys",
            messages=[{"role": "user", "content": "msg"}],
            model="gpt-4o",
        )

    call_kwargs = mock_provider.complete.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"


@pytest.mark.asyncio
async def test_llm_client_uses_default_model_from_settings():
    """LLMClient.complete uses settings.claude_model when no model is passed."""
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value="ok")

    with patch("pim_core.llm.client.get_provider", return_value=mock_provider) as mock_factory:
        from pim_core.llm.client import LLMClient
        from pim_core.config import settings
        client = LLMClient()
        await client.complete(system="sys", messages=[{"role": "user", "content": "msg"}])

    mock_factory.assert_called_once_with(settings.claude_model)
