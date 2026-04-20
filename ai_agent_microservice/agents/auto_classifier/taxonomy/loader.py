from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.auto_classifier.config import get_classifier_settings
from agents.auto_classifier.db.base import _AsyncSessionLocal, init_db
from agents.auto_classifier.db.models import TaxonomyLoad, TaxonomyNode, TaxonomyType
from agents.auto_classifier.taxonomy.custom import load_custom_nodes
from agents.auto_classifier.taxonomy.eclass import fetch_eclass_nodes
from agents.auto_classifier.taxonomy.embedder import embed_batch
from agents.auto_classifier.taxonomy.gs1 import fetch_gs1_nodes

logger = logging.getLogger(__name__)

BATCH_SIZE = 50


async def _upsert_nodes(session: AsyncSession, nodes: list[dict]) -> int:
    settings = get_classifier_settings()
    texts = [f"{n['name']} {n['breadcrumb']}" for n in nodes]
    inserted = 0

    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i : i + BATCH_SIZE]
        batch_nodes = nodes[i : i + BATCH_SIZE]
        embeddings = await embed_batch(batch_texts, model=settings.embedding_model)

        for node_data, embedding in zip(batch_nodes, embeddings):
            result = await session.execute(
                select(TaxonomyNode).where(
                    TaxonomyNode.code == node_data["code"],
                    TaxonomyNode.taxonomy_type == TaxonomyType(node_data["taxonomy_type"]),
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.name = node_data["name"]
                existing.parent_code = node_data["parent_code"] or None
                existing.breadcrumb = node_data["breadcrumb"]
                existing.embedding = embedding
            else:
                session.add(TaxonomyNode(
                    code=node_data["code"],
                    name=node_data["name"],
                    taxonomy_type=TaxonomyType(node_data["taxonomy_type"]),
                    parent_code=node_data["parent_code"] or None,
                    breadcrumb=node_data["breadcrumb"],
                    embedding=embedding,
                ))
                inserted += 1

        await session.commit()
        logger.info("Processed batch %d, total nodes so far: %d", i // BATCH_SIZE + 1, i + len(batch_nodes))

    return inserted


async def load_gs1(session: AsyncSession) -> None:
    settings = get_classifier_settings()
    logger.info("Fetching GS1 GPC taxonomy...")
    nodes = await fetch_gs1_nodes(settings.gs1_gpc_url)
    logger.info("GS1: %d nodes fetched, embedding...", len(nodes))
    inserted = await _upsert_nodes(session, nodes)
    session.add(TaxonomyLoad(taxonomy_type=TaxonomyType.gs1, node_count=len(nodes), status="success"))
    await session.commit()
    logger.info("GS1 load complete: %d new, %d updated", inserted, len(nodes) - inserted)


async def load_eclass(session: AsyncSession) -> None:
    settings = get_classifier_settings()
    logger.info("Fetching eCl@ss taxonomy...")
    nodes = await fetch_eclass_nodes(
        settings.eclass_download_url,
        settings.eclass_download_user,
        settings.eclass_download_pass,
    )
    logger.info("eCl@ss: %d nodes fetched, embedding...", len(nodes))
    inserted = await _upsert_nodes(session, nodes)
    session.add(TaxonomyLoad(taxonomy_type=TaxonomyType.eclass, node_count=len(nodes), status="success"))
    await session.commit()
    logger.info("eCl@ss load complete: %d new, %d updated", inserted, len(nodes) - inserted)


async def load_custom(session: AsyncSession, yaml_path: str = "sample_data/pim_core/auto_classifier/custom_taxonomy.yaml") -> None:
    logger.info("Loading custom taxonomy from %s...", yaml_path)
    nodes = load_custom_nodes(yaml_path)
    logger.info("Custom: %d nodes, embedding...", len(nodes))
    inserted = await _upsert_nodes(session, nodes)
    session.add(TaxonomyLoad(taxonomy_type=TaxonomyType.custom, node_count=len(nodes), status="success"))
    await session.commit()
    logger.info("Custom load complete: %d new, %d updated", inserted, len(nodes) - inserted)


async def main() -> None:
    import sys
    logging.basicConfig(level=logging.INFO)
    settings = get_classifier_settings()
    init_db(settings.database_url)

    taxonomies = sys.argv[1:] or ["gs1", "eclass", "custom"]

    assert _AsyncSessionLocal is not None
    async with _AsyncSessionLocal() as session:
        if "gs1" in taxonomies:
            await load_gs1(session)
        if "eclass" in taxonomies:
            await load_eclass(session)
        if "custom" in taxonomies:
            await load_custom(session)


if __name__ == "__main__":
    asyncio.run(main())
