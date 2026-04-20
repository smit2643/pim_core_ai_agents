from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.auth.jwt import require_scope
from agents.auto_classifier.db.base import get_session
from agents.auto_classifier.db.models import TaxonomyNode, TaxonomyType
from agents.auto_classifier.schemas.response import TaxonomyListResponse, TaxonomyNodeResponse

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.get("", response_model=TaxonomyListResponse)
async def list_taxonomy(
    taxonomy_type: TaxonomyType = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_scope("taxonomy:read")),
) -> TaxonomyListResponse:
    offset = (page - 1) * page_size
    total = (await session.execute(
        select(func.count()).where(TaxonomyNode.taxonomy_type == taxonomy_type)
    )).scalar_one()
    nodes = (await session.execute(
        select(TaxonomyNode)
        .where(TaxonomyNode.taxonomy_type == taxonomy_type)
        .order_by(TaxonomyNode.code)
        .offset(offset)
        .limit(page_size)
    )).scalars().all()

    return TaxonomyListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[TaxonomyNodeResponse.model_validate(n) for n in nodes],
    )


@router.get("/{node_id}", response_model=TaxonomyNodeResponse)
async def get_taxonomy_node(
    node_id: int,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_scope("taxonomy:read")),
) -> TaxonomyNodeResponse:
    node = (await session.execute(
        select(TaxonomyNode).where(TaxonomyNode.id == node_id)
    )).scalar_one_or_none()

    if node is None:
        raise HTTPException(status_code=404, detail="Taxonomy node not found")
    return TaxonomyNodeResponse.model_validate(node)
