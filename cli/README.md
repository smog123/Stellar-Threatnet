# Stellar ThreatNet CLI

Terminal access to the Stellar ThreatNet threat intelligence API.

## Install

```bash
cd cli
pip install -e .
```

## Configuration

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `THREATNET_API_URL` | `http://localhost:8000/api/v1` | API base URL |
| `THREATNET_API_TOKEN` | *(empty)* | JWT or API key for authenticated commands |

You can also pass `--api-url` / `--token` to every command.

## Commands

```bash
# Reputation lookups
threatnet lookup wallet GABC...1234
threatnet lookup domain stellar-fake-airdrop.com
threatnet lookup token USDC GBC...ISSUER

# Incidents & stats
threatnet incidents --status investigating --limit 20
threatnet stats

# Community reporting (requires a token)
threatnet submit domain evil-claim.net \
  --category "Fake Airdrop" \
  --description "Cloned claim page harvesting secret keys" \
  --evidence-url "https://stellar.expert/tx/..." \
  --token tn_...

# Threat feed
threatnet feed --output feed.csv

# AI assistant
threatnet ai "Is this wallet suspicious? GABC...1234"
```

## Exit behavior

- `0` — success.
- Unknown entities print a neutral notice (an untracked entity is *not* trusted).
- API errors print `error [<status>]: <detail>` and exit non-zero.

## License

MIT
