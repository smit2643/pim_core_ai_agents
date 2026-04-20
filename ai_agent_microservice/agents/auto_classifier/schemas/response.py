from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CategoryCandidate(BaseModel):
    code: str
    name: str
    breadcrumb: str = ""
    score: float


class ClassifyResult(BaseModel):
    result_id: int
    product_text: str
    taxonomy_type: str
    stage: str
    candidates: list[CategoryCandidate]
    chosen_code: str | None
    chosen_name: str | None
    confidence: float
    requires_review: bool
    reasoning: str = ""


class TaxonomyNodeResponse(BaseModel):
    id: int
    code: str
    name: str
    taxonomy_type: str
    parent_code: str | None
    breadcrumb: str

    model_config = {"from_attributes": True}


class TaxonomyListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TaxonomyNodeResponse]


class CorrectionResponse(BaseModel):
    id: int
    result_id: int
    correct_code: str
    correct_name: str
    notes: str | None
    created_at: datetime
