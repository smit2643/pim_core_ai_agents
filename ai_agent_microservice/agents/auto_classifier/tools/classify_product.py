from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.audit.logger import write_audit_record
from agents.auto_classifier.cache.redis_cache import get_cached, set_cached
from agents.auto_classifier.config import get_classifier_settings
from agents.auto_classifier.db.models import ClassificationResult, ClassificationStage, TaxonomyType
from agents.auto_classifier.schemas.response import CategoryCandidate, ClassifyResult
from agents.auto_classifier.workflows.classification_workflow import classification_graph


async def classify_product(
    product_text: str,
    taxonomy_type: str,
    top_k: int,
    min_confidence: float | None,
    session: AsyncSession,
    service_account_id: int | None = None,
) -> ClassifyResult:
    settings = get_classifier_settings()

    # Cache check
    cached = await get_cached(product_text, taxonomy_type, top_k)
    if cached:
        return ClassifyResult(**cached)

    # Run the LangGraph classification workflow
    state = await classification_graph.ainvoke({
        "product_text": product_text,
        "taxonomy_type": taxonomy_type,
        "top_k": top_k,
        "session": session,
        "candidates": [],
        "chosen_code": None,
        "chosen_name": None,
        "confidence": 0.0,
        "reasoning": "",
        "stage": "embedding",
        "error": None,
    })

    if state.get("error"):
        raise ValueError(state["error"])

    effective_threshold = min_confidence if min_confidence is not None else settings.confidence_hitl_threshold
    requires_review = state["confidence"] < effective_threshold or state["chosen_code"] is None

    stage_enum = ClassificationStage.embedding if state["stage"] == "embedding" else ClassificationStage.llm_tier2

    db_result = ClassificationResult(
        product_text=product_text,
        taxonomy_type=TaxonomyType(taxonomy_type),
        stage=stage_enum,
        chosen_code=state["chosen_code"],
        chosen_name=state["chosen_name"],
        confidence=state["confidence"],
        requires_review=requires_review,
        service_account_id=service_account_id,
    )
    session.add(db_result)
    await session.commit()
    await session.refresh(db_result)

    await write_audit_record(
        session=session,
        result_id=db_result.id,
        event="classify",
        payload={
            "stage": state["stage"],
            "confidence": state["confidence"],
            "requires_review": requires_review,
            "reasoning": state["reasoning"],
        },
    )

    output = ClassifyResult(
        result_id=db_result.id,
        product_text=product_text,
        taxonomy_type=taxonomy_type,
        stage=state["stage"],
        candidates=[
            CategoryCandidate(
                code=c["code"],
                name=c["name"],
                breadcrumb=c["breadcrumb"],
                score=c["score"],
            )
            for c in state["candidates"]
        ],
        chosen_code=state["chosen_code"],
        chosen_name=state["chosen_name"],
        confidence=state["confidence"],
        requires_review=requires_review,
        reasoning=state["reasoning"],
    )

    if not requires_review:
        await set_cached(product_text, taxonomy_type, top_k, output.model_dump(), ttl=settings.cache_ttl_seconds)

    return output
