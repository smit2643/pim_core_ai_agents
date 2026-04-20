from __future__ import annotations

import hashlib
import json
from typing import Any

from redis.asyncio import Redis, from_url

_redis: Redis | None = None


async def init_redis(redis_url: str) -> Redis:
    global _redis
    _redis = await from_url(redis_url, decode_responses=True)
    return _redis


def get_redis() -> Redis:
    assert _redis is not None, "Redis not initialised"
    return _redis


def _cache_key(product_text: str, taxonomy_type: str, top_k: int) -> str:
    digest = hashlib.sha256(product_text.encode()).hexdigest()
    return f"cls:{taxonomy_type}:{top_k}:{digest}"


async def get_cached(product_text: str, taxonomy_type: str, top_k: int) -> Any | None:
    key = _cache_key(product_text, taxonomy_type, top_k)
    raw = await get_redis().get(key)
    return json.loads(raw) if raw is not None else None


async def set_cached(
    product_text: str,
    taxonomy_type: str,
    top_k: int,
    value: Any,
    ttl: int = 86_400,
) -> None:
    key = _cache_key(product_text, taxonomy_type, top_k)
    await get_redis().set(key, json.dumps(value), ex=ttl)
