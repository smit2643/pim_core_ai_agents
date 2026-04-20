# pim_core — Shared Infrastructure

Shared code used by all agents. Nothing in here is specific to any one agent.

## Modules

| Module | Purpose |
|--------|---------|
| `config.py` | pydantic-settings `Settings` singleton — reads env vars |
| `llm/` | Provider-agnostic LLM abstraction layer |
| `schemas/` | Pydantic models shared across agents |

## Key rule

Never import from `agents/` here. This package is consumed by agents, not the other way around.
