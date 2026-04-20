from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine: AsyncEngine | None = None
_AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str) -> AsyncEngine:
    global _engine, _AsyncSessionLocal
    _engine = create_async_engine(database_url, echo=False, pool_pre_ping=True)
    _AsyncSessionLocal = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    assert _AsyncSessionLocal is not None, "DB not initialised — call init_db() at startup"
    async with _AsyncSessionLocal() as session:
        yield session
