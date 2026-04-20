from __future__ import annotations

from typing import Any

_SYSTEM_PROMPT = """\
You are a product category classifier for a PIM (Product Information Management) system.

Your job:
1. Understand what the product is from whatever data is provided
2. Assign the most accurate category based on the taxonomy standard requested

Rules:
- Analyse ALL provided product fields to understand what the product is
- Ignore empty, null, or irrelevant fields
- Return ONLY valid JSON — no extra text

Response format:
{"code": "<category_code>", "name": "<category_name>", "confidence": <0.0-1.0>, "reasoning": "<brief reason>"}

Taxonomy behaviour:
- GS1: Return the official GS1 Global Product Classification code and full category name
- eCl@ss: Return the official eCl@ss code and category name
- custom: Return code as null — return a clear, logical category name based on what the product is

Confidence guide:
- 0.90-1.0: Product is clearly identifiable, category is obvious
- 0.70-0.89: Good match but some ambiguity in product data
- 0.50-0.69: Limited product data, best guess
- Below 0.50: Very unclear product, low confidence\
"""


def get_system_prompt() -> str:
    return _SYSTEM_PROMPT


def get_user_message(product: dict[str, Any], taxonomy_type: str) -> str:
    # Extract all non-empty fields from whatever the client sends
    filled = {
        k: v
        for k, v in product.items()
        if v is not None and v != "" and v != 0 and v is not False
    }

    product_lines = "\n".join(f"  {k}: {v}" for k, v in filled.items())

    taxonomy_instruction = {
        "gs1": "Classify into the GS1 Global Product Classification standard. Return the GS1 segment/family/class/brick code and name.",
        "eclass": "Classify into the eCl@ss standard. Return the eCl@ss code and name.",
        "custom": "Classify into a logical category based on what this product is. Return code as null and a clear descriptive category name.",
    }.get(taxonomy_type, f"Classify into the {taxonomy_type.upper()} taxonomy standard.")

    return (
        f"Product data:\n{product_lines}\n\n"
        f"Taxonomy: {taxonomy_type.upper()}\n"
        f"{taxonomy_instruction}"
    )
