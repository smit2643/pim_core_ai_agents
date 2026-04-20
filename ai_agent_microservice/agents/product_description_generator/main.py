from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.product_description_generator.routes.agent_registry import router as agent_registry_router
from agents.product_description_generator.routes.model_config import router as model_config_router
from agents.product_description_generator.routes.pim_ingest import router as pim_ingest_router
from agents.product_description_generator.tools.generate_description import generate_description
from pim_core.schemas.product import BrandVoice, DescriptionResult, Product

app = FastAPI(title="Product Description Generator Agent", version="1.0.0")
app.include_router(model_config_router)
app.include_router(pim_ingest_router)
app.include_router(agent_registry_router)


class GenerateDescriptionRequest(BaseModel):
    product: Product
    channel: str
    brand_voice: BrandVoice | None = None


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "agent": "content"}


@app.post("/generate-description", response_model=DescriptionResult)
async def generate_description_endpoint(
    request: GenerateDescriptionRequest,
) -> DescriptionResult:
    try:
        return await generate_description(
            product=request.product,
            channel=request.channel,
            brand_voice=request.brand_voice,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
