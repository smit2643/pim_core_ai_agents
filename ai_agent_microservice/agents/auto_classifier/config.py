from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ClassifierSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    classifier_model: str = "claude-sonnet-4-6"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/auto_classifier"

    # Redis
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 86400  # 24h

    # Confidence thresholds
    confidence_auto_accept: float = 0.95   # write immediately, no HITL
    confidence_write: float = 0.75         # write but flag for sample review

    log_level: str = "INFO"


settings = ClassifierSettings()
