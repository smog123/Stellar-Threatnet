# stellar-threatnet-sdk

Official Python SDK for the [Stellar ThreatNet](https://github.com/stellar-threatnet/stellar-threatnet) API.

## Install

```bash
pip install -e ./sdks/python   # from the repo root
```

## Quick start

```python
import asyncio
from stellar_threatnet_sdk import ThreatNetClient


async def main():
    # Anonymous (rate limited) or with an API key:
    # client = ThreatNetClient(api_key="tn_...")
    async with ThreatNetClient() as client:
        try:
            result = await client.lookup_wallet("GABC...123")
            print(result["status"], result["reputation_score"])
        except Exception as e:
            print("unknown/neutral:", e)  # HTTP 404 = no data

        stats = await client.stats()
        print(stats)

        threats = await client.latest_threats(limit=5)
        for t in threats:
            print(t["entity_type"], t["identifier"], t["status"])


asyncio.run(main())
```

## Methods

| Method | Endpoint |
| --- | --- |
| `lookup_wallet(address)` | `GET /lookup/wallet/{address}` |
| `lookup_domain(domain)` | `GET /lookup/domain/{domain}` |
| `lookup_token(code, issuer)` | `GET /lookup/token/{code}/{issuer}` |
| `incidents(status, limit, offset)` | `GET /incidents` |
| `incident(id)` | `GET /incidents/{id}` |
| `latest_threats(limit)` | `GET /threats/latest` |
| `stats()` | `GET /stats` |
| `search(query, type, limit)` | `GET /search` |
| `download_feed(path)` | `GET /feed` (CSV) |
| `submit_report(type, value, description, ...)` | `POST /reports` |
| `ai_query(query)` | `POST /ai/query` |

Treat an HTTP 404 on lookups as **no data** (neutral), never as trusted.

## License

MIT
