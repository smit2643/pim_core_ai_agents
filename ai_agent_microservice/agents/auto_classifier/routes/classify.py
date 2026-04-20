from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.auth.jwt import require_scope
from agents.auto_classifier.db.base import get_session
from agents.auto_classifier.schemas.request import ClassifyRequest
from agents.auto_classifier.schemas.response import ClassifyResult
from agents.auto_classifier.tools.classify_product import classify_product

router = APIRouter(prefix="/classify", tags=["classify"])


@router.post("", response_model=ClassifyResult)
async def classify(
    body: ClassifyRequest,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(require_scope("classify:write")),
) -> ClassifyResult:
    try:
        sa_id = int(token_data["sub"]) if token_data.get("sub") else None
    except (TypeError, ValueError):
        sa_id = None

    try:
        return await classify_product(
            product_text=body.product_text,
            taxonomy_type=body.taxonomy_type,
            top_k=body.top_k,
            min_confidence=body.min_confidence,
            session=session,
            service_account_id=sa_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
