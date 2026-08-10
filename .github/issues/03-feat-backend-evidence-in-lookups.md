# feat(backend): include evidence items in lookup responses

## Summary

Wallet, domain, and token lookup responses currently omit the evidence records
that justify a reputation score. Include an `evidence` array (proof type, URL,
confidence, verified flag) so clients can surface the reasoning behind a score.

## Why it matters

Explainable scores are a core ThreatNet promise. Showing evidence is what
converts a number into a decision users can trust.

## Acceptance Criteria

- [ ] Lookup responses include an `evidence` array when records exist
- [ ] Only evidence appropriate for public consumption is returned
- [ ] Pydantic schemas and SQLAlchemy queries are updated accordingly
- [ ] Tests cover empty, single, and multi-evidence cases
- [ ] `docs/API.md` shows the new response shape

## Tech Stack

Python 3.11 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · pytest
