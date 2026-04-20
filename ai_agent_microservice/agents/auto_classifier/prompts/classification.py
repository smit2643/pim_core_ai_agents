from __future__ import annotations

import json
from typing import Any

_SYSTEM_PROMPT = """\
You are a product category classifier for a PIM system.

Given a product in JSON format, identify what the product is and classify it into the most accurate category.

Return ONLY this JSON — no other text:
{
  "category_path": "<top level> > <mid level> > <specific category>",
  "code": "<taxonomy code or null>",
  "confidence": <0.0 to 1.0>,
  "reasoning": "<one sentence why>"
}

Notes:
- category_path must always be a hierarchical path using " > " as separator
- For GS1 and eCl@ss: fill code from your knowledge of that standard
- For custom taxonomy: set code to null, focus on a clear descriptive category_path
- confidence reflects how clearly the product data identifies the category\
"""


def get_system_prompt() -> str:
    return _SYSTEM_PROMPT


def _clean_product(product: dict[str, Any]) -> dict[str, Any]:
    """Remove only empty/null/false values. LLM decides what's relevant."""
    return {
        k: v
        for k, v in product.items()
        if v is not None and v != "" and v != 0 and v != 0.0 and v is not False
    }


def get_user_message(product: dict[str, Any], taxonomy_type: str) -> str:
    cleaned = _clean_product(product)
    product_json = json.dumps(cleaned, indent=2, default=str)

    return (
        f"Taxonomy: {taxonomy_type.upper()}\n\n"
        f"Product:\n{product_json}"
    )
