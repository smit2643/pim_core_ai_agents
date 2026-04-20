# tests — Test Suite

pytest suite mirroring the source tree. All async tests run automatically (asyncio_mode=auto in pytest.ini).

## Structure

| Path | Covers |
|------|--------|
| `conftest.py` | Shared fixtures: `sample_product`, `sample_brand_voice`; sets `ANTHROPIC_API_KEY` env var |
| `test_config.py` | `pim_core/config.py` |
| `test_schemas.py` | `pim_core/schemas/product.py` |
| `test_llm_client.py` | `pim_core/llm/client.py` |
| `test_llm_factory.py` | `pim_core/llm/factory.py` |
| `test_llm_registry.py` | `pim_core/llm/registry.py` |
| `content/test_brand_voice.py` | `agents/content/prompts/brand_voice.py` |
| `content/test_description_workflow.py` | `agents/content/workflows/description_workflow.py` |
| `content/test_generate_description_tool.py` | `agents/content/tools/generate_description.py` |
| `content/test_model_config.py` | `agents/content/routes/model_config.py` |
| `content/test_main.py` | `agents/content/main.py` (integration) |

## Running

```bash
# Full suite
venv/bin/python -m pytest tests/ -v

# Single file
venv/bin/python -m pytest tests/content/test_description_workflow.py -v
```

## LLM calls

All LLM calls are mocked. Tests never hit real APIs.
The mock path is always: `agents.content.workflows.description_workflow.llm_client.complete`
