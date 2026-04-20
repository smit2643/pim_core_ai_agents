from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ClassifierSettings(BaseSettings):
    """Settings specific to the auto-classifier agent.

    Shared LLM keys (anthropic_api_key, openai_api_key, google_api_key) are
    read from pim_core.config.settings — not duplicated here.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database (postgres + pgvector)
    database_url: str = "postgresql+asyncpg://classifier:classifier@localhost:5432/classifier"

    # Redis
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 86_400

    # LLM — model name drives provider selection via pim_core factory
    llm_tier2_model: str = "claude-sonnet-4-6"

    # Embedding (always OpenAI)
    embedding_model: str = "text-embedding-3-small"

    # Confidence thresholds
    confidence_embedding_threshold: float = 0.92
    confidence_hitl_threshold: float = 0.75

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Taxonomy sources
    gs1_gpc_url: str = ""
    eclass_download_url: str = ""
    eclass_download_user: str = ""
    eclass_download_pass: str = ""

    log_level: str = "INFO"


@lru_cache(maxsize=1)
def get_classifier_settings() -> ClassifierSettings:
    return ClassifierSettings()
