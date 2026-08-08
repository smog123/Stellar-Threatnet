# feat(backend): wire real AI providers (OpenAI/Anthropic/Ollama) with guardrails

## Summary

Implement the provider adapters behind the existing modular LLM interface in
`backend/app/services/threat_engine.py`, selectable via the `AI_PROVIDER`
environment variable, with structured fallback prompting and the existing
confidence-disclaimer guardrails.

## Why it matters

The AI assistant currently ships with a `mock` provider. Real providers turn
`POST /ai/query` into a useful investigation aid while the guardrails keep it
from asserting certainty without evidence.

## Acceptance Criteria

- [ ] Adapters for `openai`, `anthropic`, and `ollama` implement the same interface
- [ ] `AI_PROVIDER` switches providers at runtime; unknown values fail fast
- [ ] Prompt guardrails are enforced for every provider (no certainty claims without evidence)
- [ ] Provider failure falls back to `mock` with a clear error signal
- [ ] Tests use a fake provider; no real API keys are required to test

## Tech Stack

Python 3.11 · httpx · Pydantic Settings · pytest
