from __future__ import annotations

from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None

BATCH_SIZE = 50


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


async def embed_text(text: str, model: str = "text-embedding-3-small") -> list[float]:
    resp = await _get_client().embeddings.create(input=text, model=model)
    return resp.data[0].embedding


async def embed_batch(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    if not texts:
        return []
    resp = await _get_client().embeddings.create(input=texts, model=model)
    return [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]
