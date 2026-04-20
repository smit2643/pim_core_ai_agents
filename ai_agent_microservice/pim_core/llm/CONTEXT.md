# pim_core/llm — LLM Abstraction Layer

Provides a single `llm_client` that works with any supported LLM provider.

## Files

| File | Purpose |
|------|---------|
| `client.py` | `LLMClient` — provider-agnostic wrapper; delegates to factory |
| `factory.py` | `get_provider(model_name)` — selects and caches provider by model prefix |
| `registry.py` | `AgentModelRegistry` — maps agent names to model strings at runtime |
| `providers/base.py` | `BaseLLMProvider` abstract class |
| `providers/anthropic_provider.py` | Claude (claude-*) |
| `providers/openai_provider.py` | GPT (gpt-*, o1-*, o3-*) |
| `providers/google_provider.py` | Gemini (gemini-*) |

## Model name → provider routing

- `claude-*` → `AnthropicProvider` (requires `ANTHROPIC_API_KEY`)
- `gpt-*`, `o1-*`, `o3-*`, `o4-*` → `OpenAIProvider` (requires `OPENAI_API_KEY`)
- `gemini-*` → `GoogleProvider` (requires `GOOGLE_API_KEY`)

## Adding a new provider

1. Create `providers/yourprovider.py` implementing `BaseLLMProvider`
2. Add a prefix branch in `factory.py`
3. Add the API key field to `pim_core/config.py`
