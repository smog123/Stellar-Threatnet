# End-User Guides

Three guides, one per persona. Plain language, concrete endpoints. The scoring
model behind everything here is `docs/THREAT_MODEL.md`.

Live API base URL: `https://stellar-threatnet-api.onrender.com/api/v1`
Live dashboard: `https://stellar-threatnet.vercel.app`

Seeded demo accounts (password for all: `threatnet-demo`):
`admin@stellar-threatnet.org`, `analyst@stellar-threatnet.org`,
`moderator@stellar-threatnet.org`, `reporter@stellar-threatnet.org`.

---

## Guide 1 — Reporting a threat (Community Reporter)

**Who this is for:** anyone who spots a suspicious wallet, phishing domain, or
fake token on Stellar.

**Why reporting matters:** every approved report attaches evidence to the
target and moves its reputation score. One report alone never changes a score —
moderation does. That keeps one person from weaponizing reputation.

### 1. Create an account

```bash
curl -X POST https://stellar-threatnet-api.onrender.com/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password","full_name":"You"}'
```

Or use the seeded reporter account:
`reporter@stellar-threatnet.org` / `threatnet-demo`.

### 2. Submit a report

Open the dashboard **Community** page (`/community`) and fill in the
"Submit a threat report" form, or call the API:

```bash
curl -X POST https://stellar-threatnet-api.onrender.com/api/v1/reports \
  -H 'Authorization: Bearer <your-jwt>' \
  -H 'Content-Type: application/json' \
  -d '{
    "target_type": "domain",
    "target_value": "claim-xlm-rewards.xyz",
    "category": "Fake Airdrop",
    "description": "Claim page in a memo-phishing wave. Harvests secret keys.",
    "evidence_url": "https://stellar.expert/tx/demo"
  }'
```

Rules for the target value:

- **Wallet:** a Stellar public key, `G...`, 56 characters.
- **Domain:** the domain name as written. Seeded homograph indicators use
  their punycode form (e.g. `xn--stellr-mta.com`).
- **Token:** `CODE:ISSUER` — both parts required. `FAKEUSDC:GD3...` not
  `FAKEUSDC`.

You get a report ID like `REP-1A2B3C4D`. Its status is `pending`.

### 3. What happens next

1. **Pending** — the report sits in the moderation queue. Anyone can upvote
   or downvote it (one vote per account):

   ```bash
   curl -X POST https://stellar-threatnet-api.onrender.com/api/v1/reports/{id}/vote \
     -H 'Authorization: Bearer <your-jwt>' \
     -H 'Content-Type: application/json' \
     -d '{"vote": "up"}'
   ```
2. **Approved** — a moderator accepts it with a proof type and confidence.
   Evidence is attached to the target and its score is recomputed.
3. **Rejected** — the moderator records why.

An approved report changes lookups, the threat feed, and the dashboard within
seconds (lookup cache TTL is 15 minutes).

### Honesty rules

- Do not fabricate evidence URLs. Moderators check them.
- Do not include secret keys or personal data in descriptions.
- A report with no evidence is still useful as a lead — the `other` proof
  type exists for it — but it carries less weight.

---

## Guide 2 — Moderating reports (Moderator)

**Who this is for:** moderators and admins reviewing the community queue.
Moderation is the only path that changes reputation scores. Every decision is
appended to the audit log — moderation is append-only.

### 1. View the queue

```bash
curl https://stellar-threatnet-api.onrender.com/api/v1/reports/queue \
  -H 'Authorization: Bearer <moderator-jwt>'
```

Returns pending reports, oldest first.

### 2. Approve or reject

```bash
curl -X POST https://stellar-threatnet-api.onrender.com/api/v1/reports/{id}/moderate \
  -H 'Authorization: Bearer <moderator-jwt>' \
  -H 'Content-Type: application/json' \
  -d '{
    "action": "approve",
    "moderation_note": "Confirmed via live page + wallet-connect check",
    "proof_type": "domain_screenshot",
    "confidence": 0.9
  }'
```

### 3. Choose proof type and confidence honestly

Proof types and their score weights (from `threat_engine.py`):

| Proof type | Weight |
| --- | ---: |
| `onchain_proof` | 50 |
| `payload_sample` | 40 |
| `tx_hash` | 30 |
| `domain_screenshot` | 25 |
| `multi_source` | 20 |
| `other` | 15 |

Confidence levels (from `THREAT_MODEL.md`):

| Level | Meaning | Confidence |
| --- | --- | ---: |
| 1 | Unverified community report | 0.3 |
| 2 | Multiple independent sources | 0.6 |
| 3 | Manually verified by an analyst | 0.9 |
| 4 | On-chain proof / audit finding | 1.0 |

Defaults when you omit them: proof type `other`, confidence `0.9`. Only choose
`onchain_proof` when you actually verified it on-ledger.

### 4. What approving does

1. Validates the target format (a token without `CODE:ISSUER` returns 422).
2. Attaches an `Evidence` row with your proof type, confidence, and note.
3. Recomputes the entity's score: `80 − Σ(weight × confidence) + 20 if verified`,
   clamped to [0, 100]. Worked arithmetic is in `THREAT_MODEL.md` §5.
4. Writes `REPORT_APPROVED` to the append-only audit log.

Rejecting records a `REPORT_REJECTED` audit entry and changes nothing else.

---

## Guide 3 — Integrating ThreatNet (Developer / Security Team)

**Who this is for:** wallet, exchange, dApp, and research teams that want to
consume threat intelligence.

### 1. Lookups — the core call

| Entity | Endpoint |
| --- | --- |
| Wallet | `GET /lookup/wallet/{address}` → `reputation_score` (0–100), `status` |
| Domain | `GET /lookup/domain/{domain}` → `confidence_score` (0–1), `status` |
| Token | `GET /lookup/token/{code}/{issuer}` → `confidence_score`, `status` |

```bash
curl https://stellar-threatnet-api.onrender.com/api/v1/lookup/wallet/GABC...DEF
```

```json
{
  "address": "GABC...DEF",
  "reputation_score": 10,
  "status": "confirmed_malicious",
  "category": "Malicious Drainer",
  "reason": "Confirmed drainer behavior across multiple accounts.",
  "report_count": 14
}
```

`404` means **unknown** — treat as neutral, never as trusted. `400` means the
input was malformed.

### 2. Act on the status

| Status | Action |
| --- | --- |
| `confirmed_malicious` | BLOCK transaction / navigation |
| `suspicious` | WARN with a high-risk confirmation |
| `under_investigation` | Show an informational badge |
| `trusted` | ALLOW |

### 3. Feed, stats, search

- `GET /feed` — full CSV of wallets, domains, tokens (rate limit 30/min).
- `GET /threats/latest` — recent non-trusted entities.
- `GET /stats` — global counts.
- `GET /search?q={query}` — multi-entity search.

### 4. Authenticate for write operations

- Interactive: `POST /auth/token` → JWT → `Authorization: Bearer <jwt>`.
- Programmatic: `POST /api-keys` → `X-API-Key: tn_...`. The plaintext key is
  shown exactly once; keys are stored as SHA-256 hashes.

### 5. Zero-trust verification on-chain

The Soroban registry stores only SHA-256 hashes of indicators. To verify
without trusting the API:

1. Hash the identifier with SHA-256 → 32 bytes.
2. Call `get_threat_indicator(hash)` on the deployed testnet contract
   `CB34YG3ZGQ3FGK32D6GMMFKKK4SPWN5QURF4VCCQ67ZHBILJBH2KBCG5`
   (`https://stellar.expert/explorer/testnet/contract/CB34YG3ZGQ3FGK32D6GMMFKKK4SPWN5QURF4VCCQ67ZHBILJBH2KBCG5`).
3. A record exists → the indicator was confirmed and published by the admin.

The TypeScript pattern for reads is in
`docs/wave/APP_AGENT_SYSTEM_PROMPT.md` §7. Publishing new hashes to the
contract is a planned feature (backend admin-publish issue) — the registry is
currently readable, not yet written to from the API.

### 6. Client libraries

- Python SDK: `pip install stellar-threatnet-sdk` (see `sdks/python/`).
- TypeScript SDK: `@stellar-threatnet/sdk` (see `sdks/javascript/`).
- CLI: `threatnet lookup wallet GABC...DEF` (see `cli/`).
- Browser extension: Manifest V3 warning overlay (see `browser-extension/`).

### 7. Rate limits

Per IP: lookups 120/min, feed 30/min, AI queries 20/min, register 5/min,
login 10/min. Over the limit returns `429`.
