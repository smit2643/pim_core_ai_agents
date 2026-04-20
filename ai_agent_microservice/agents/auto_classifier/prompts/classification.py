from __future__ import annotations

_SYSTEM_PROMPT = """\
You are a product taxonomy classifier. Given a product description and a list of \
candidate taxonomy categories, select the best matching category.

Respond ONLY with valid JSON in this exact format:
{"code": "<category_code>", "name": "<category_name>", "confidence": <0.0-1.0>, "reasoning": "<brief reason>"}

If no candidate is a good match, respond:
{"code": null, "name": null, "confidence": 0.0, "reasoning": "<why none match>"}

Do not include any text outside the JSON object.\
"""


def get_system_prompt() -> str:
    return _SYSTEM_PROMPT


def get_user_message(product_text: str, candidates: list[dict]) -> str:
    candidates_text = "\n".join(
        f"  {i + 1}. [{c['code']}] {c['name']} — {c['breadcrumb']} (embedding score: {c['score']:.3f})"
        for i, c in enumerate(candidates)
    )
    return (
        f"Product description:\n{product_text}\n\n"
        f"Candidate categories:\n{candidates_text}\n\n"
        "Select the best category or return null if none match."
    )
