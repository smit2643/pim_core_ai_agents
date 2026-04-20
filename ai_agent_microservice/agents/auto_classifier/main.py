from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from agents.auto_classifier.audit.logger import configure_logging
from agents.auto_classifier.cache.redis_cache import init_redis
from agents.auto_classifier.config import get_classifier_settings
from agents.auto_classifier.db.base import init_db
from agents.auto_classifier.routes.classify import router as classify_router
from agents.auto_classifier.routes.corrections import router as corrections_router
from agents.auto_classifier.routes.health import router as health_router
from agents.auto_classifier.routes.model_config import router as model_config_router
from agents.auto_classifier.routes.taxonomy import router as taxonomy_router
from agents.auto_classifier.workflows.classification_workflow import AGENT_NAME
from pim_core.llm.registry import agent_model_registry

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    cfg = get_classifier_settings()

    engine = init_db(cfg.database_url)
    redis = await init_redis(cfg.redis_url)

    # Register this agent's model in the shared registry
    agent_model_registry.set(AGENT_NAME, cfg.llm_tier2_model)

    logger.info("auto_classifier startup complete", model=cfg.llm_tier2_model)
    try:
        yield
    finally:
        await engine.dispose()
        await redis.aclose()
        logger.info("auto_classifier shutdown complete")


app = FastAPI(
    title="Auto Classifier Agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(model_config_router)
app.include_router(classify_router)
app.include_router(taxonomy_router)
app.include_router(corrections_router)
