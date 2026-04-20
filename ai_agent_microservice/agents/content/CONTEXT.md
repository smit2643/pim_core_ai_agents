# agents/content — Content & Enrichment Agent

FastAPI microservice (port 8002) that generates SEO-optimised product descriptions.

## Entry point

`main.py` — mounts all routers and exposes the FastAPI `app`.

## Request flow

```
POST /generate-description
  → generate_description tool (tools/generate_description.py)
    → LangGraph StateGraph (workflows/description_workflow.py)
      → agent_model_registry.get("content") → resolve current model
        → llm_client.complete(model=...) → provider → LLM API
```

## Config API

`POST /config/model {"model": "gpt-4o"}` — sets the LLM for this agent at runtime.
`GET  /config/model` — returns current model assignment.

## Agent name

This agent is registered in `AgentModelRegistry` under the key `"content"`.
