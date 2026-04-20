from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.cache.redis_cache import get_redis
from agents.auto_classifier.db.base import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(session: AsyncSession = Depends(get_session)) -> dict:
    db_ok = False
    try:
        await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    redis_ok = False
    try:
        await get_redis().ping()
        redis_ok = True
    except Exception:
        pass

    return {
        "status": "ok" if db_ok and redis_ok else "degraded",
        "agent": "auto_classifier",
        "db": db_ok,
        "redis": redis_ok,
    }
