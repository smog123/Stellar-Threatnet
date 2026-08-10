# feat(backend): filter the CSV threat feed by entity type

## Summary

`GET /feed` currently exports wallets, domains, and tokens together in one CSV.
Add a `?type=wallet|domain|token` query parameter (repeatable or
comma-separated) so consumers can request only the entity types they need.

## Why it matters

Different integrations consume different slices of the feed — a wallet
integration does not want token rows. Filtering keeps feeds small and focused.

## Acceptance Criteria

- [ ] `?type=wallet` returns only wallet rows (same for `domain`, `token`)
- [ ] Multiple types are OR'd together
- [ ] Invalid or empty type values return a clear 422/400 response
- [ ] Unit tests cover each type and combinations
- [ ] `docs/API.md` documents the parameter

## Tech Stack

Python 3.11 · FastAPI · CSV streaming · pytest
