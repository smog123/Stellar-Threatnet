# Developer Guide

## Repository layout

```
backend/                 FastAPI service (Python 3.11+)
  app/core/              config, security, rate limiting
  app/db/                async SQLAlchemy engine & session
  app/models/            ORM entities (users, wallets, domains, tokens, ...)
  app/schemas/           Pydantic request/response models
  app/services/          threat engine, cache, Celery tasks
  app/api/v1/            routers, dependencies, endpoints
  tests/                 pytest suite (in-memory SQLite)
  alembic/               migrations
# (Soroban contract lives in stellar-threatnet-contract — separate repo)
frontend/                Next.js 14 dashboard (TypeScript, Tailwind)
cli/                     Python CLI (click + httpx)
sdks/                    Python and TypeScript SDKs
browser-extension/       Manifest V3 warning extension
docs/                    architecture, threat model, API, deployment
```

## Backend architecture

```
Endpoints (FastAPI) -> ThreatService (business logic) -> SQLAlchemy (async) -> PostgreSQL
                          |-> cache (Redis, graceful fallback)
                          |-> audit log (append-only)
                          |-> Celery tasks (scores, Horizon polling)
```

### The scoring pipeline

1. A community report is submitted (`reporter`).
2. A `moderator` approves it → an `Evidence` row is attached to the entity.
3. `ThreatService.recompute_entity_score()` runs the formula from
   `docs/THREAT_MODEL.md`:
   `S(E) = 80 - Σ(W_i × C_i) + 20(verified)`, clamped to [0, 100].
4. Derived status: 0–20 confirmed malicious, 21–50 suspicious, 51–79 under
   investigation, 80–100 trusted.

Evidence weights live in `backend/app/services/threat_engine.py`
(`EVIDENCE_WEIGHTS`). **Changing weights is a security-relevant change** —
requires two maintainer reviews.

### Adding an endpoint

1. Add a service method in `threat_engine.py` (keep endpoints thin).
2. Add request/response schemas in `app/schemas/threats.py`.
3. Register the route in `app/api/v1/endpoints/threats.py` (or a new module +
   `app/api/v1/router.py`).
4. Write API tests in `backend/tests/` — lookups 404 for unknown entities,
   RBAC 403 for the wrong role, moderation recomputes scores.
5. `pytest` must pass.

### Testing

Tests use an in-memory SQLite DB (see `tests/conftest.py`), with rate limiting
and caching disabled via env vars. Each test gets a fresh DB.

```bash
cd backend
.venv/bin/python -m pytest -q
```

## Frontend architecture

Next.js App Router, client components for interactive pages, `src/lib/api.ts`
for API access (set `NEXT_PUBLIC_API_URL`). Pages are server components by
default and fetch via the API client.

## Soroban contract

`#![no_std]`, `soroban-sdk 27.0.5`, wasm target `wasm32v1-none`. Key design
point: only **hashes** of indicators are stored on-ledger; raw intelligence
stays off-chain in the API database. The contract lives in the separate
`stellar-threatnet-contract` repository (this repo links to it).

## Conventions

- Python: typed, async-first; no sync DB access in request paths.
- SQLAlchemy 2.0 style; `Enum` columns for statuses.
- Commit messages: `feat(backend): add X`, `fix(contract): ...`,
  `docs(frontend): ...`.
- Run `cargo fmt` / `cargo clippy` for contract changes.
