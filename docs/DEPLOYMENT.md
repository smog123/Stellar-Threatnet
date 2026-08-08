# Deployment Guide

## Architecture

```
[ TLS ] -> [ NGINX/Cloudflare ] -> [ FastAPI (xN) ] -> PostgreSQL 15
                                      |      \-> Redis 7 (cache + broker)
                                      \-> Celery workers -> Horizon (optional)
```

## Quick start (Docker Compose)

```bash
cp .env.example .env          # then edit secrets
docker compose up -d --build
```

Services:
- Backend + Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`, Redis: `localhost:6379`

## Production checklist

1. **Secrets**: set a long random `SECRET_KEY` (>= 32 bytes). Never ship the
   default value.
2. **Database migrations**:

   ```bash
   cd backend
   .venv/bin/alembic revision --autogenerate -m "initial"
   .venv/bin/alembic upgrade head
   ```

   (Development `docker compose` auto-creates tables for convenience; production
   must use Alembic.)
3. **Reverse proxy**: terminate TLS at NGINX/Cloudflare. Set
   `CORS_ORIGINS` to your dashboard origin.
4. **Redis** is used for both caching and Celery. Without it the API still
   works (graceful fallback to PostgreSQL) but background jobs are disabled.
5. **Workers**:

   ```bash
   docker compose exec worker celery -A app.services.tasks worker --loglevel=info --beat
   ```
6. **Backups**: `pg_dump` daily; test restores. Audit logs must never be
   truncated by application code.
7. **Monitoring**: expose `/health` to your orchestrator; alert on 429 spikes
   (possible API abuse) and on worker queue growth.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `ENV` | `development` | `production` enables fail-fast checks (weak `SECRET_KEY` refused) |
| `SECRET_KEY` | *dev only* | JWT signing secret |
| `DATABASE_URL` | local asyncpg URL | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Cache + Celery broker |
| `CACHE_TTL_SECONDS` | `900` | Lookup cache TTL |
| `RATE_LIMIT_ENABLED` | `true` | Master switch for rate limiting |
| `AI_PROVIDER` | `mock` | `mock`, `openai`, `anthropic`, `ollama` |
| `CORS_ORIGINS` | localhost list | Allowed dashboard origins (JSON array) |

## Scaling

- Backend is stateless → scale horizontally behind a load balancer.
- Read-heavy lookups hit Redis (15-min TTL) with PostgreSQL fallback; add
  read replicas when the write/read ratio degrades.
- Run one Celery beat scheduler only; workers scale independently.

## Soroban contract deployment

```bash
cd contracts/soroban_threatnet
rustup target add wasm32v1-none
cargo build --target wasm32v1-none --release
# deploy with soroban-cli (scripts/deploy.sh), then call initialize(admin)
```

The contract stores SHA-256 hashes of confirmed indicators on-ledger for
zero-trust client verification. The contract now lives in the separate
`stellar-threatnet-contract` repository — see its `README.md` and `SPEC.md`.
For the full hosting picture (frontend on Vercel, backend + DB on Render),
see [docs/WAVE_TOPOLOGY.md](WAVE_TOPOLOGY.md).
