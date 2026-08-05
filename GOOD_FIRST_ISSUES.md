# Good First Issues

Welcome! This file lists starter tasks sized for first-time contributors to
Stellar ThreatNet. Each item links to a repo area; search the issue tracker for
matching `good first issue` labels.

## Backend (Python / FastAPI)

- **Add a new threat category** — extend `backend/app/models/entities.py` and
  the schemas with a new category (e.g. `FAKE_EXCHANGE`), then add a unit test.
- **Paginate the moderation queue** — `GET /reports/queue` currently returns up
  to 50 items with no pagination. Add `limit`/`offset` like `/incidents`.
- **CSV feed filters** — add `?type=wallet|domain|token` filtering to
  `GET /feed` in `backend/app/api/v1/endpoints/threats.py`.
- **Evidence display in lookups** — return attached evidence items in the
  wallet/domain/token lookup responses.

## Soroban contract (Rust)

- **Bulk publish** — add `publish_many` to
  `contracts/soroban_threatnet/src/lib.rs` for batched indicator updates.
- **Event emission** — emit Soroban events on publish for indexers.

## Frontend (Next.js / TypeScript)

- **Dark-mode toggle** — the dashboard is dark-first; add a theme switcher.
- **Lookup result copy button** — add "copy result to clipboard" micro-interactions.
- **Client-side search box** on the dashboard calling `GET /search`.

## Docs

- **API examples** — add `curl` examples to `docs/API.md` for every endpoint.
- **Deployment recipes** — add Fly.io, Render, or Railway deployment guides to
  `docs/DEPLOYMENT.md`.

## Testing & tooling

- **Coverage report** — wire `pytest --cov` into CI and add a coverage badge.
- **Contract integration test** — exercise `publish` → `get` round-trip against
  a local Soroban sandbox.

## How to claim

1. Comment on the issue: "I'd like to take this."
2. Follow [CONTRIBUTING.md](CONTRIBUTING.md) for setup.
3. Open a PR; CI must pass.

Don't see your niche? Propose a new good first issue in GitHub Discussions.
