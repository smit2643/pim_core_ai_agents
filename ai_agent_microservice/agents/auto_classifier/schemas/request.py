from typing import Annotated, Literal

from pydantic import BaseModel, Field

TaxonomyTypeLiteral = Literal["gs1", "eclass", "custom"]


class ClassifyRequest(BaseModel):
    product_text: str = Field(..., min_length=1, max_length=4096)
    taxonomy_type: TaxonomyTypeLiteral = "gs1"
    top_k: Annotated[int, Field(ge=1, le=5)] = 3
    min_confidence: float | None = None


class CorrectionRequest(BaseModel):
    result_id: int
    correct_code: str
    correct_name: str
    notes: str | None = None
