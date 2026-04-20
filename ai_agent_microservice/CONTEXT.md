# ai_agent_microservice

Root of the PIM-AI agent microservice. Each agent is a FastAPI app inside `agents/`. Shared infrastructure lives in `pim_core/`.

## Structure

| Directory | Purpose |
|-----------|---------|
| `pim_core/` | Shared config, LLM client, provider abstraction, agent model registry, Pydantic schemas |
| `agents/` | One subdirectory per agent — each is a standalone FastAPI app |
| `tests/` | pytest suite mirroring the source tree |

## Running tests

```bash
venv/bin/python -m pytest tests/ -v
```

## Running the Content Agent

```bash
venv/bin/python -m uvicorn agents.product_description_generator.main:app --reload --port 8002
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `OPENAI_API_KEY` | No | OpenAI API key (only if using GPT models) |
| `GOOGLE_API_KEY` | No | Google AI API key (only if using Gemini models) |
| `ENVIRONMENT` | No | `development` (default) or `production` |
| `LOG_LEVEL` | No | `INFO` (default) |
