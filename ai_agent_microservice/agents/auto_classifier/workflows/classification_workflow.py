from __future__ import annotations

import json
import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.config import get_classifier_settings
from agents.auto_classifier.prompts.classification import get_system_prompt, get_user_message
from agents.auto_classifier.taxonomy.embedder import embed_text
from pim_core.llm.client import llm_client
from pim_core.llm.registry import agent_model_registry

logger = logging.getLogger(__name__)

AGENT_NAME = "auto_classifier"


class ClassificationState(TypedDict):
    product_text: str
    taxonomy_type: str
    top_k: int
    session: AsyncSession
    # outputs
    candidates: list[dict]
    chosen_code: str | None
    chosen_name: str | None
    confidence: float
    reasoning: str
    stage: str
    error: str | None


async def embedding_search_node(state: ClassificationState) -> dict:
    """Run HNSW cosine similarity search and return top-k candidates."""
    settings = get_classifier_settings()
    session: AsyncSession = state["session"]

    embedding = await embed_text(state["product_text"], model=settings.embedding_model)
    vector_literal = "[" + ",".join(str(v) for v in embedding) + "]"

    sql = text(
        """
        SELECT id, code, name, breadcrumb,
               1 - (embedding <=> :vec ::vector) AS score
        FROM taxonomy_nodes
        WHERE taxonomy_type = :ttype
        ORDER BY embedding <=> :vec ::vector
        LIMIT :top_k
        """
    )
    result = await session.execute(
        sql,
        {"vec": vector_literal, "ttype": state["taxonomy_type"], "top_k": state["top_k"]},
    )
    rows = result.fetchall()
    candidates = [
        {"id": r.id, "code": r.code, "name": r.name, "breadcrumb": r.breadcrumb, "score": float(r.score)}
        for r in rows
    ]

    logger.info(
        "Embedding search for '%s' → %d candidates, top score %.3f",
        state["product_text"][:60],
        len(candidates),
        candidates[0]["score"] if candidates else 0.0,
    )
    return {"candidates": candidates, "stage": "embedding"}


def _should_call_llm(state: ClassificationState) -> str:
    settings = get_classifier_settings()
    top_score = state["candidates"][0]["score"] if state["candidates"] else 0.0
    return "done" if top_score >= settings.confidence_embedding_threshold else "llm"


async def llm_classify_node(state: ClassificationState) -> dict:
    """Call the assigned LLM to pick the best candidate from embedding results."""
    model = agent_model_registry.get(AGENT_NAME)
    system = get_system_prompt()
    user = get_user_message(state["product_text"], state["candidates"])

    logger.info("Calling LLM model '%s' for classification", model)

    try:
        raw = await llm_client.complete(
            system=system,
            messages=[{"role": "user", "content": user}],
            model=model,
            max_tokens=512,
        )
        parsed = json.loads(raw)
        return {
            "chosen_code": parsed.get("code"),
            "chosen_name": parsed.get("name"),
            "confidence": float(parsed.get("confidence", 0.0)),
            "reasoning": parsed.get("reasoning", ""),
            "stage": "llm_tier2",
            "error": None,
        }
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("LLM parse failed: %s", exc)
        return {
            "chosen_code": None,
            "chosen_name": None,
            "confidence": 0.0,
            "reasoning": "LLM returned invalid response",
            "stage": "llm_tier2",
            "error": str(exc),
        }


async def embedding_accept_node(state: ClassificationState) -> dict:
    """Accept the top embedding result directly (score above threshold)."""
    best = state["candidates"][0]
    return {
        "chosen_code": best["code"],
        "chosen_name": best["name"],
        "confidence": best["score"],
        "reasoning": "Embedding similarity above auto-accept threshold",
        "error": None,
    }


def build_classification_graph():
    graph: StateGraph = StateGraph(ClassificationState)

    graph.add_node("embedding_search", embedding_search_node)
    graph.add_node("llm_classify", llm_classify_node)
    graph.add_node("embedding_accept", embedding_accept_node)

    graph.set_entry_point("embedding_search")
    graph.add_conditional_edges(
        "embedding_search",
        _should_call_llm,
        {"llm": "llm_classify", "done": "embedding_accept"},
    )
    graph.add_edge("llm_classify", END)
    graph.add_edge("embedding_accept", END)

    return graph.compile()


classification_graph = build_classification_graph()
