from __future__ import annotations

import logging

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.config import get_classifier_settings
from agents.auto_classifier.db.models import ClassificationAudit


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(get_classifier_settings().log_level)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
    )


async def write_audit_record(
    *,
    session: AsyncSession,
    result_id: int,
    event: str,
    payload: dict,
) -> None:
    record = ClassificationAudit(result_id=result_id, event=event, payload=payload)
    session.add(record)
    await session.flush()
