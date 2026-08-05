# @stellar-threatnet/sdk

Official TypeScript SDK for the [Stellar ThreatNet](https://github.com/stellar-threatnet/stellar-threatnet) API.

## Install

```bash
npm install        # from ./sdks/javascript (or via your registry once published)
```

## Quick start

```typescript
import { ThreatNetClient } from "@stellar-threatnet/sdk";

// Anonymous, or with an API key:
// const client = new ThreatNetClient({ apiKey: "tn_..." });
const client = new ThreatNetClient();

try {
  const wallet = await client.lookupWallet("GABC...123");
  console.log(wallet.status, wallet.reputation_score);
} catch (err) {
  // 404 = no data -> treat as neutral, never as trusted
  console.log("unknown/neutral:", err);
}

const stats = await client.stats();
console.log(stats);

const threats = await client.latestThreats(5);
for (const t of threats) console.log(t.entity_type, t.identifier, t.status);
```

## API

| Method | Endpoint |
| --- | --- |
| `lookupWallet(address)` | `GET /lookup/wallet/{address}` |
| `lookupDomain(domain)` | `GET /lookup/domain/{domain}` |
| `lookupToken(code, issuer)` | `GET /lookup/token/{code}/{issuer}` |
| `incidents(status?, limit, offset)` | `GET /incidents` |
| `incident(id)` | `GET /incidents/{id}` |
| `latestThreats(limit)` | `GET /threats/latest` |
| `stats()` | `GET /stats` |
| `search(query, type?, limit)` | `GET /search` |
| `downloadFeed()` | `GET /feed` (CSV text) |
| `submitReport(...)` | `POST /reports` |
| `aiQuery(query)` | `POST /ai/query` |

## License

MIT
