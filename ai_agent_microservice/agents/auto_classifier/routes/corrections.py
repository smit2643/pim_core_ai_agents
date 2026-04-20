from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.audit.logger import write_audit_record
from agents.auto_classifier.auth.jwt import require_scope
from agents.auto_classifier.db.base import get_session
from agents.auto_classifier.db.models import ClassificationResult, Correction
from agents.auto_classifier.schemas.request import CorrectionRequest
from agents.auto_classifier.schemas.response import CorrectionResponse

router = APIRouter(prefix="/corrections", tags=["corrections"])


@router.post("", response_model=CorrectionResponse, status_code=201)
async def submit_correction(
    body: CorrectionRequest,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_scope("classify:write")),
) -> CorrectionResponse:
    classification = (await session.execute(
        select(ClassificationResult).where(ClassificationResult.id == body.result_id)
    )).scalar_one_or_none()

    if classification is None:
        raise HTTPException(status_code=404, detail="Classification result not found")

    correction = Correction(
        result_id=body.result_id,
        correct_code=body.correct_code,
        correct_name=body.correct_name,
        notes=body.notes,
    )
    session.add(correction)
    classification.requires_review = False
    await session.commit()
    await session.refresh(correction)

    await write_audit_record(
        session=session,
        result_id=body.result_id,
        event="correction",
        payload={"correct_code": body.correct_code, "correct_name": body.correct_name, "notes": body.notes},
    )

    return CorrectionResponse(
        id=correction.id,
        result_id=correction.result_id,
        correct_code=correction.correct_code,
        correct_name=correction.correct_name,
        notes=correction.notes,
        created_at=correction.created_at,
    )
