# pim_core — Shared Infrastructure

Shared code used by all agents. Nothing in here is specific to any one agent.

## Modules

| Module | Purpose |
|--------|---------|
| `config.py` | pydantic-settings `Settings` singleton — reads env vars |
| `llm/` | Provider-agnostic LLM abstraction layer |
| `schemas/product.py` | `Product`, `ProductAttributes`, `BrandVoice`, `DescriptionResult` — normalised data contracts |
| `schemas/pim_product.py` | `PIMProductRecord` — mirrors all ~50 raw PIM export fields. `extra = "allow"` ensures unknown fields don't fail validation |
| `adapters/pim_adapter.py` | `pim_record_to_product()` — maps a raw `PIMProductRecord` to the normalised `Product` schema. Strips trailing spaces, filters empty image URLs, skips descriptions identical to the product name |
| `utils/all_available_models.py` | `AllAvailableModelsAnthropic`, `AllAvailableModelsOpenAI`, `AllAvailableModelsGoogle` — enums that are the single source of truth for every supported model name. factory.py and agent_registry.py derive their logic from these. |
| `utils/all_agents.py` | `AllAgents` — enum of every registered agent. **Register a new agent here first** before writing any agent code. Used everywhere instead of bare string literals. |
| `db/agent_model_db.py` | SQLite persistence — `load_all()`, `upsert()`, `delete()` for agent→model assignments. The registry loads from here on startup; writes go here immediately. |

## Key rule

Never import from `agents/` here. This package is consumed by agents, not the other way around.
