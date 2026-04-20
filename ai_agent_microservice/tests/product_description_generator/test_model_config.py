import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from pim_core.utils.all_agents import AllAgents

AGENT_KEY = AllAgents.PRODUCT_DESCRIPTION_GENERATOR.value


@pytest.mark.asyncio
async def test_get_model_returns_default():
    """GET /config/model returns the default Claude model when none is set."""
    from pim_core.llm.registry import agent_model_registry
    agent_model_registry.remove(AGENT_KEY)

    from agents.product_description_generator.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/config/model")

    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == AGENT_KEY
    assert data["model"].startswith("claude-")


@pytest.mark.asyncio
async def test_set_model_stores_and_returns_new_model():
    """POST /config/model updates the registry and returns the new assignment."""
    with patch("agents.product_description_generator.routes.model_config.get_provider"):
        from agents.product_description_generator.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/config/model", json={"model": "gpt-4o"})

    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == AGENT_KEY
    assert data["model"] == "gpt-4o"


@pytest.mark.asyncio
async def test_set_model_persists_for_subsequent_get():
    """After POST, GET /config/model reflects the new model."""
    with patch("agents.product_description_generator.routes.model_config.get_provider"):
        from agents.product_description_generator.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/config/model", json={"model": "gemini-1.5-pro"})
            response = await client.get("/config/model")

    assert response.json()["model"] == "gemini-1.5-pro"


@pytest.mark.asyncio
async def test_set_model_rejects_unknown_prefix():
    """POST /config/model with unrecognised model returns 400."""
    from agents.product_description_generator.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/config/model", json={"model": "llama3-70b"})

    assert response.status_code == 400
    assert "No provider found" in response.json()["detail"]
