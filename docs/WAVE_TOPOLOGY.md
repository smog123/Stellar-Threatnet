# Hosting & Service Topology

Where each piece of Stellar ThreatNet lives, and why. Read this before touching
deployment config.

## Final topology

```
                          ┌──────────────────────┐
                          │   Community users    │
                          └──────────┬───────────┘
                                     │ HTTPS
        ┌────────────────────────────┼─────────────────────────────┐
        ▼                            ▼                             ▼
┌────────────────┐          ┌──────────────────┐          ┌─────────────────┐
│  Browser       │          │  Frontend        │          │  CLI / SDKs     │
│  Extension     │          │  Next.js 14      │          │  (user side)    │
│  (client-side) │          │  on Vercel       │          │                 │
└────────────────┘          └────────┬─────────┘          └─────────────────┘
        │                            │ NEXT_PUBLIC_API_URL (build-time)
        │                            ▼
        │                 ┌──────────────────┐        ┌──────────────────┐
        │                 │  FastAPI Backend │        │  Soroban RPC     │
        │                 │  on Render       │        │  (contract reads │
        │                 └───────┬──────────┘        │   & writes,      │
        │                         │                   │   zero-trust)    │
        │                         │                   └────────┬─────────┘
        │                         ▼                            │
        │                 ┌──────────────────┐                 │
        │                 │ PostgreSQL 15    │                 │
        │                 │ (Render, same    │                 ▼
        │                 │  region, private │        ┌──────────────────┐
        │                 │  connection)     │        │ Stellar Soroban  │
        │                 └──────────────────┘        │ contract (ledger)│
        │                         ▲                    └──────────────────┘
        │                         │ Redis 7 (cache + Celery broker)
        │                         └──────────────────────┘
```

Data flows:

1. **User → frontend (Vercel).** Dashboard pages fetch reputation data through
   `NEXT_PUBLIC_API_URL`. Vercel serves static/SSR output; it holds no state.
2. **Frontend → backend (Render).** All lookups, incidents, reports, stats go
   through the REST API. Public endpoints are rate limited (slowapi).
3. **Frontend → Soroban RPC directly (optional).** For zero-trust contract
   verification, the dashboard can call the contract via `@stellar/stellar-sdk`
   without going through our API. This is the "trust the ledger" path.
4. **Backend → PostgreSQL (Render).** The database is provisioned alongside the
   backend service, same region, using the **internal/private connection
   string** — never the public one.
5. **Backend → Redis.** Cache (15-min TTL, graceful fallback) and Celery broker.
   Without Redis the API still works; background jobs are disabled.
6. **Backend → Horizon.** Live ledger stream (opt-in `INGESTOR_ENABLED=true`)
   flags threats in real time; per-request Horizon fallback profiles unknown
   wallets.

## Why this split

- **Frontend on Vercel:** purpose-built for Next.js; deploys on push, serves
  edge-cached. Do not migrate it to Render just because the backend lives there.
- **Backend on Render:** a stateful long-running service with workers and a
  database — Render's model fits. `render.yaml` pins the language, root
  directory, build command, and start command.
- **Database beside the backend:** same region, private connection string,
  lower latency and no public exposure.

## Common failure: frontend calling localhost in production

Symptom: dashboard works locally, returns network errors in production. Root
cause: `NEXT_PUBLIC_API_URL` is a **build-time** variable — it must be set in
the Vercel project's environment variable UI before build, not just in a local
`.env.local`. Fix it at the source (set the variable + redeploy), not by
hardcoding URLs.

## Production checklist (current state)

- Backend: `https://stellar-threatnet-api.onrender.com` (docs at `/docs`)
- Frontend: `https://frontend-rosy-five-50.vercel.app`
- Contract: deploy via `stellar-threatnet-contract/scripts/deploy.sh`, then set
  `SOROBAN_RPC_URL` + `THREATNET_CONTRACT_ID` in Vercel and Render env UIs.
