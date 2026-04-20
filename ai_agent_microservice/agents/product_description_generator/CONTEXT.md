# agents/product_description_generator — Product Description Generator Agent

FastAPI microservice (port 8002) that generates SEO-optimised product descriptions.

## Entry point

`main.py` — mounts all routers and exposes the FastAPI `app`.

## Request flows

```
POST /generate-description              ← accepts a pre-normalised Product schema
  → generate_description tool (tools/generate_description.py)
    → LangGraph StateGraph (workflows/description_workflow.py)
      → agent_model_registry.get("content") → resolve current model
        → llm_client.complete(model=...) → provider → LLM API

POST /pim/generate-description          ← accepts a raw PIM export record
  → pim_record_to_product() (pim_core/adapters/pim_adapter.py)
    → generate_description tool (same pipeline as above)
```

## Config API

`POST /config/model {"model": "gpt-4o"}` — sets the LLM for this agent at runtime.
`GET  /config/model` — returns current model assignment.

## Routes

| Route | File | Purpose |
|-------|------|---------|
| `POST /generate-description` | `main.py` | Accepts a normalised `Product` + channel |
| `POST /pim/generate-description` | `routes/pim_ingest.py` | Accepts a raw PIM record, adapts it, then generates |
| `POST /config/model` | `routes/model_config.py` | Switch active LLM for the "content" agent |
| `GET  /config/model` | `routes/model_config.py` | Read current LLM for the "content" agent |
| `GET  /models/available` | `routes/agent_registry.py` | List all supported models by provider |
| `POST /agents/{name}/model` | `routes/agent_registry.py` | Assign any model to any agent by name |
| `GET  /agents/models` | `routes/agent_registry.py` | View all agent → model assignments + default |
| `DELETE /agents/{name}/model` | `routes/agent_registry.py` | Reset an agent to the default model |

## Agent name

This agent is registered in `AgentModelRegistry` under the key `"content"`.
