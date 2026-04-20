# agents — Agent Microservices

Each subdirectory is a self-contained FastAPI microservice for one PIM-AI agent.

## Current agents

| Agent | Port | Purpose |
|-------|------|---------|
| `content/` | 8002 | Content & Enrichment — generates product descriptions, enriches sparse records |

## Planned agents (future)

| Agent | Purpose |
|-------|---------|
| `catalog/` | Catalog Management — classifies, tags, sequences images |
| `procurement/` | Procurement/Buying — searches catalog, raises POs |

## Conventions

Every agent directory contains:
- `main.py` — FastAPI app instance
- `tools/` — FastMCP tools (the agent's callable actions)
- `workflows/` — LangGraph StateGraphs (the agent's reasoning loops)
- `prompts/` — Prompt template builders (separated from execution logic)
- `routes/` — FastAPI routers for admin/config endpoints

## Agent identity in the model registry

The agent name string used in `AgentModelRegistry` matches the directory name.
Content agent → `"content"`. Catalog agent (future) → `"catalog"`.
