# ThreatNet REST API

Base URL: `http://localhost:8000/api/v1` (production: `https://stellar-threatnet-api.onrender.com/api/v1`)

Interactive docs: `GET /docs` (Swagger UI) and `GET /redoc`.

All requests and responses are JSON (`text/csv` for the feed). Pagination is
`offset`/`limit` based. Errors use RFC 7807-style `{"detail": "..."}` bodies.

## Authentication

| Method | Auth | Description |
| --- | --- | --- |
| `POST /auth/register` | public | Create an account (role: reporter) |
| `POST /auth/token` | public | OAuth2 password login → JWT |
| `GET /auth/me` | **JWT or API key** | Current user profile |

Two credential formats are supported:

- `Authorization: Bearer <jwt>` — interactive clients
- `X-API-Key: tn_...` — programmatic clients / SDKs

## Roles

| Role | Permissions |
| --- | --- |
| `read_only` | lookups, feed, stats |
| `reporter` | + submit reports, vote |
| `moderator` | + moderate reports, update incidents |
| `analyst` | + create incidents |
| `admin` | + audit logs, user management |

## Reputation lookups

### `GET /lookup/wallet/{address}`

Reputation for a Stellar public key (`G...`, 56 chars).

```bash
curl http://localhost:8000/api/v1/lookup/wallet/GABC...DEF
```

```json
{
  "address": "GABC...DEF",
  "reputation_score": 10,
  "status": "confirmed_malicious",
  "category": "Malicious Drainer",
  "reason": "Confirmed drainer behavior across multiple accounts.",
  "report_count": 14,
  "last_updated": "2026-08-05T10:00:00Z"
}
```

### `GET /lookup/domain/{domain}`

Phishing/impersonation score for a domain. Returns `confidence_score` (0.0–1.0).

### `GET /lookup/token/{asset_code}/{issuer}`

Token reputation keyed by `CODE:ISSUER`.

`404` with `"No threat data found..."` means the entity is **unknown** — treat
as neutral, never as trusted. `400` means invalid input format.

## Incidents

| Method | Endpoint | Auth |
| --- | --- | --- |
| `GET` | `/incidents?status=&severity=&limit=&offset=` | public |
| `GET` | `/incidents/{id}` | public |
| `POST` | `/incidents` | analyst+ |
| `PATCH` | `/incidents/{id}` | moderator+ |

Incident fields: `title`, `description`, `affected_services`, `mitigations`,
`references`, `severity` (`critical|high|medium|low`), `status`
(`open|investigating|resolved|dismissed`).

## Feed, threats, stats, search

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/threats/latest?limit=` | Recent non-trusted entities |
| `GET` | `/feed` | Full CSV threat feed (wallets, domains, tokens) |
| `GET` | `/stats` | Global dashboard metrics |
| `GET` | `/search?q=&type=&limit=` | Search wallets, domains, tokens, incidents |

## Community reports & moderation

| Method | Endpoint | Auth |
| --- | --- | --- |
| `POST` | `/reports` | authenticated |
| `POST` | `/reports/{id}/vote` | authenticated (`{"vote": "up"|"down"}`) |
| `GET` | `/reports/queue` | moderator+ |
| `POST` | `/reports/{id}/moderate` | moderator+ |

Moderate payload:

```json
{
  "action": "approve",
  "moderation_note": "Confirmed via on-chain tx trace",
  "proof_type": "tx_hash",
  "confidence": 1.0
}
```

Approving attaches an evidence record to the target entity and **recomputes its
reputation score** using the formula in `docs/THREAT_MODEL.md`.

## AI threat assistant

### `POST /ai/query`

```json
{"query": "Is this wallet suspicious? GABC...DEF", "context_type": "general"}
```

Always returns `confidence_disclaimer` — the assistant never claims certainty
without evidence.

## API keys

| Method | Endpoint | Auth |
| --- | --- | --- |
| `POST` | `/api-keys` `{"name": "ci"}` | authenticated |
| `GET` | `/api-keys` | authenticated |
| `DELETE` | `/api-keys/{id}` | authenticated (owner) |

The plaintext key (`tn_...`) is returned **exactly once** — store it securely.
Keys are stored hashed (SHA-256).

## Audit log

`GET /admin/audit-logs?action=&limit=` — **admin only**. Append-only record of
score changes, moderation decisions, incident edits, and key management.

## Rate limiting

Public endpoints are rate limited per IP (slowapi): lookups `120/min`, feed
`30/min`, AI queries `20/min`, register `5/min`, login `10/min`. Limit
headers are returned in responses. Over the limit returns `429`.
