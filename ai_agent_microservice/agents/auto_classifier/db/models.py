import enum
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey,
    Index, Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agents.auto_classifier.db.base import Base


class TaxonomyType(str, enum.Enum):
    gs1 = "gs1"
    eclass = "eclass"
    custom = "custom"


class ClassificationStage(str, enum.Enum):
    embedding = "embedding"
    llm_tier2 = "llm_tier2"


class TaxonomyNode(Base):
    __tablename__ = "taxonomy_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    taxonomy_type: Mapped[TaxonomyType] = mapped_column(Enum(TaxonomyType), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    breadcrumb: Mapped[str] = mapped_column(Text, nullable=False, default="")
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_taxonomy_code_type", "code", "taxonomy_type", unique=True),
        Index("ix_taxonomy_type", "taxonomy_type"),
        Index(
            "ix_taxonomy_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_text: Mapped[str] = mapped_column(Text, nullable=False)
    taxonomy_type: Mapped[TaxonomyType] = mapped_column(Enum(TaxonomyType), nullable=False)
    stage: Mapped[ClassificationStage] = mapped_column(Enum(ClassificationStage), nullable=False)
    chosen_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    chosen_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    requires_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    service_account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("service_accounts.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Correction(Base):
    __tablename__ = "corrections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classification_results.id"), nullable=False
    )
    correct_code: Mapped[str] = mapped_column(String(100), nullable=False)
    correct_name: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClassificationAudit(Base):
    __tablename__ = "classification_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classification_results.id"), nullable=False
    )
    event: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TaxonomyLoad(Base):
    __tablename__ = "taxonomy_loads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    taxonomy_type: Mapped[TaxonomyType] = mapped_column(Enum(TaxonomyType), nullable=False)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ServiceAccount(Base):
    __tablename__ = "service_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    hashed_secret: Mapped[str] = mapped_column(Text, nullable=False)
    scopes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
