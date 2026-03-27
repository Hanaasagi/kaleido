## intent-classifier

Two-stage intent-first conversational library:

1. Call LLM #1 to infer structured intent/strategy JSON.
2. Inject this analysis into LLM #2 for a human-like response.
3. Apply an autonomy policy so replies do not always blindly agree.

The CLI prints stage-1 JSON and stage-2 streaming response for inspection.

## Quickstart (uv)

```bash
uv sync
export OPENAI_API_KEY="your_key"
# Optional:
# export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
# export ANALYSIS_MODEL="openai/gpt-4.1-mini"
# export RESPONSE_MODEL="openai/gpt-4.1-mini"
uv run intent-chat
```

## Environment Variables

- `OPENAI_API_KEY` (required)
- `OPENAI_BASE_URL` (default: `https://openrouter.ai/api/v1`)
- `ANALYSIS_MODEL` (default: `openai/gpt-4.1-mini`)
- `RESPONSE_MODEL` (default: `openai/gpt-4.1-mini`)
- `ANALYSIS_TEMPERATURE` (default: `0.1`)
- `RESPONSE_TEMPERATURE` (default: `0.8`)
- `PERSONA_PATH` (default: `config/personas/girlfriend.toml`)

## Project Layout

```text
src/intent_classifier/
  cli.py
  config.py
  llm_client.py
  models.py
  orchestrator.py
  persona.py
  prompts.py
config/personas/girlfriend.toml
```
