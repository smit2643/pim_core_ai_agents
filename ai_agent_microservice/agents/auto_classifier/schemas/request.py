from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

TaxonomyType = Literal["gs1", "eclass", "custom"]


class ClassifyRequest(BaseModel):
    product: dict[str, Any]   # any shape — whatever the client sends
    taxonomy_type: TaxonomyType = "gs1"
