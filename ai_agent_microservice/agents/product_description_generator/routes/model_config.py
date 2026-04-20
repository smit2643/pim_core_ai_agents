from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pim_core.llm.factory import get_provider
from pim_core.llm.registry import agent_model_registry
from pim_core.utils.all_agents import AllAgents

router = APIRouter(prefix="/config", tags=["configuration"])

AGENT_NAME = AllAgents.PRODUCT_DESCRIPTION_GENERATOR


class SetModelRequest(BaseModel):
    model: str


class ModelResponse(BaseModel):
    agent: str
    model: str


@router.get("/model", response_model=ModelResponse)
async def get_model() -> ModelResponse:
    """Return the LLM model currently assigned to the product description generator agent."""
    return ModelResponse(agent=AGENT_NAME.value, model=agent_model_registry.get(AGENT_NAME.value))


@router.post("/model", response_model=ModelResponse)
async def set_model(request: SetModelRequest) -> ModelResponse:
    """Assign an LLM model to the product description generator agent.

    The model takes effect on the next generate-description call.
    No service restart is required. The assignment is persisted to SQLite.

    Raises:
        400: If the model is not listed in any AllAvailableModels* enum.
    """
    try:
        get_provider(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    agent_model_registry.set(AGENT_NAME.value, request.model)
    return ModelResponse(agent=AGENT_NAME.value, model=request.model)
