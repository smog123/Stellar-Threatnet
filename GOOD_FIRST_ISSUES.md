# Good First Issues

Welcome! This file lists starter tasks sized for first-time contributors to
Stellar ThreatNet. Every item maps to a planned issue in `.github/issues/` —
create the batch with `make issues` (requires `gh` + auth), then pick one with
the `good first issue` label.

## Backend (Python / FastAPI)

- **Paginate the moderation queue** — `GET /reports/queue` returns up to 50
  items with no pagination. Add `limit`/`offset` like `/incidents`.
- **Filter the CSV threat feed** — add `?type=wallet|domain|token` filtering to
  `GET /feed` in `backend/app/api/v1/endpoints/threats.py`.
- **Evidence in lookups** — return attached evidence items in the
  wallet/domain/token lookup responses.
- **New threat categories** — extend `backend/app/models/entities.py` and the
  schemas with new categories (e.g. `FAKE_EXCHANGE`, `CLONE_APP`), plus seed data.

## Soroban contract (Rust)

- **Bulk publish** — add `publish_many` to
  `contracts/soroban_threatnet/src/lib.rs` for batched indicator updates.
- **Event emission** — emit Soroban events on publish for indexers.
- **Round-trip integration test** — exercise `publish` → `get` against a local
  Soroban sandbox as a CI job.

## Frontend (Next.js / TypeScript)

- **Copy result button** — add "copy result to clipboard" with visible feedback
  on the lookup result cards.

## Docs

- **API examples** — add `curl` examples to `docs/API.md` for every endpoint.
- **Deployment recipes** — add Fly.io and Railway deployment guides to
  `docs/DEPLOYMENT.md`.

## Testing & tooling

- **Coverage report** — wire `pytest --cov` into CI, enforce a threshold, and
  add a coverage badge.

## How to claim

1. Run `make issues` (requires `gh` + auth) to create the planned issues, or
   browse the existing `good first issue` labels.
2. Comment on the issue: "I'd like to take this."
3. Follow [CONTRIBUTING.md](CONTRIBUTING.md) for setup.
4. Open a PR; CI must pass.

Don't see your niche? Propose a new good first issue in GitHub Discussions.
