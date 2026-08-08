<div align="center">

<img src="assets/banner.svg" alt="Stellar ThreatNet — Open Threat Intelligence for the Stellar Ecosystem" width="100%">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI Pipeline](https://github.com/smog123/stellar-threatnet-app/actions/workflows/ci.yml/badge.svg)](https://github.com/smog123/stellar-threatnet-app/actions)
[![CodeQL Security Audit](https://github.com/smog123/stellar-threatnet-app/actions/workflows/codeql.yml/badge.svg)](https://github.com/smog123/stellar-threatnet-app/actions)
[![Backend Tests](https://img.shields.io/badge/tests-45%20passing-brightgreen.svg)](backend/tests/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Community](https://img.shields.io/badge/Community-Discussions-8b5cf6.svg)](https://github.com/smog123/stellar-threatnet-app/discussions)

# 🛡️ Stellar ThreatNet

> **Open-Source Shared Security & Threat Intelligence Infrastructure for the Stellar Ecosystem.**

[Live Dashboard](https://stellar-threatnet.vercel.app) · [Live API Docs](https://stellar-threatnet-api.onrender.com/docs) · [GitHub Repository](https://github.com/smog123/stellar-threatnet-app)

</div>

---

## 📌 Executive Summary

**Stellar ThreatNet** is the first open-source, decentralized threat intelligence platform built specifically for the **Stellar blockchain ecosystem**.

In Web3 security, malicious actors frequently deploy credential-harvesting phishing domains, automated wallet drainers, fake airdrop tokens, and scam DEX liquidity pools. **ThreatNet solves this by serving as the underlying security intelligence layer** — collecting, validating, scoring, and distributing reputation data on malicious Stellar wallet addresses, domains, and tokens.

> 💡 **What ThreatNet Is and Is Not:**
> - **IS:** The security intelligence layer underneath Web3 applications (wallets, exchanges, dApps, block explorers, browser extensions, and security researchers).
> - **IS NOT:** A crypto wallet, a blockchain explorer, or an antivirus application.

---

## ✨ Features & Capabilities

- 🎯 **Multi-Entity Reputation Scoring (0–100):** Real-time mathematical scoring for Stellar Wallets (`G...`), Phishing Domains (`*.com`), and Fake Tokens (`CODE:ISSUER`).
- 👥 **Community & Peer-Reviewed Moderation:** Decentralized threat reporting with community upvoting/downvoting and moderator evidence verification.
- ⛓️ **Soroban On-Chain Registry:** Cryptographically anchors SHA-256 threat indicator hashes directly onto the Stellar ledger for zero-trust client validation.
- 🛡️ **Automated Threat Ingestor:** Continuous polling of public threat feeds (PhishFort, EtherScamDB, URLhaus, OpenPhish) mapped into Stellar-native indicators.
- ⚡ **High-Performance Caching & Rate Limiting:** Redis-backed caching (`< 15ms` lookup latency) and sliding window rate limiting.
- 🔌 **Developer Ecosystem Integrations:** Official Python SDK (`stellar-threatnet-sdk`), TypeScript/JS SDK (`@stellar-threatnet/sdk`), Manifest V3 Chrome Extension, and `threatnet` terminal CLI tool.

---

## 🏗️ Core Architecture & Data Flow

```
                                  ┌───────────────────────────────┐
                                  │   Automated Threat Ingestor   │
                                  │ (PhishFort / URLhaus / Feeds) │
                                  └───────────────┬───────────────┘
                                                  │
┌─────────────────────────┐                       ▼                       ┌─────────────────────────┐
│     Community User      │ ──────►  [ Submit Threat Report ]  ◄──────    │    Security Analyst     │
│   (Web Dashboard / CLI) │                                               │  (Moderation Interface) │
└─────────────────────────┘                       │                       └─────────────────────────┘
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    FastAPI Security Engine    │
                                  │   (JWT Auth, Scoring, Rate)   │
                                  └───────────────┬───────────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    ▼                             ▼                             ▼
       ┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
       │   PostgreSQL Database   │   │  Redis Distributed Cache│   │  Soroban Smart Contract │
       │  (Threats/Reports/Logs) │   │   (Sub-15ms Reputation) │   │ (On-Chain SHA-256 Hash) │
       └─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘
                                                  │
                                                  ▼
                                 ┌────────────────────────────────┐
                                 │   Downstream Integrations      │
                                 │ Wallets / Extensions / dApps   │
                                 └────────────────────────────────┘
```

---

## 🧮 Reputation Scoring Engine

Reputation scores range from **0** (Confirmed Malicious) to **100** (Verified Safe / Trusted):

| Score Range | Reputation Status | Action Recommended for Integrators |
| :--- | :--- | :--- |
| **0 – 20** | `malicious` | **BLOCK** transaction / navigation immediately |
| **21 – 50** | `suspicious` | **WARN** user with high-risk confirmation modal |
| **51 – 79** | `under_investigation` | Display informational badge |
| **80 – 100** | `trusted` | **ALLOW** normal operation |

### **Mathematical Scoring Formula**

Reputation scores are dynamically recalculated from attached evidence weights ($W_i$) and confidence coefficients ($C_i$):

$$S(E) = \max\left(0, \min\left(100, 80 - \sum (W_i \times C_i) + 20 \cdot \mathbf{1}_{\text{verified}}\right)\right)$$

* **Base Reputation:** Default initial score is 80 (Neutral).
* **Evidence Deductions ($W_i$):** On-chain proof (weight 50), payload sample (weight 40), transaction hash (weight 30), screenshot (weight 25).
* **Confidence ($C_i$):** Ranges from `0.3` (unverified report) to `1.0` (cryptographic proof).
* **Verified Boost:** $+20$ points for official ecosystem partner verification.

---

## ⛓️ Soroban Smart Contract (On-Chain Registry)

The Soroban smart contract allows zero-trust clients to verify indicator hashes directly on the Stellar ledger. It lives in its own repository — **`stellar-threatnet-contract`** (Rust, soroban-sdk 27, wasm target `wasm32v1-none`).

### **Contract Methods**
- `initialize(admin: Address)` — Sets the admin authority (single execution safety).
- `publish_threat_indicator(admin: Address, hash: BytesN<32>, level: u32, score: u32)` — Admin-gated publication of indicator hash.
- `get_threat_indicator(hash: BytesN<32>) -> Option<Indicator>` — On-chain lookup.
- `get_total_indicators() -> u32` — Returns total indicators registered on-chain.

> 🔒 **Privacy Guarantee:** Raw wallet addresses or domain names are never stored on the public blockchain — only cryptographic SHA-256 hashes are recorded.

---

## 📁 Repository Structure

```text
stellar-threatnet-app/
├── backend/                 # FastAPI service (Python 3.11+, async SQLAlchemy, Celery)
├── frontend/                # Next.js 14 Dashboard (TypeScript, Tailwind CSS)
├── cli/                     # Python-based CLI tool for threat interaction
├── docs/                    # Architecture diagrams & documentation
├── assets/                  # Logos and branding
└── docker-compose.yml       # Production/Development container setup
```

---

## 📋 Quick Start Guide

### 🚀 Live Deployed Environments

| Deployment Platform | Service | Live Endpoint / URL |
| :--- | :--- | :--- |
| **Vercel** | Frontend Dashboard | [https://stellar-threatnet.vercel.app](https://stellar-threatnet.vercel.app) |
| **Render** | FastAPI Backend & OpenAPI Docs | [https://stellar-threatnet-api.onrender.com/docs](https://stellar-threatnet-api.onrender.com/docs) |
| **Render** | REST API Base Endpoint | [https://stellar-threatnet-api.onrender.com/api/v1](https://stellar-threatnet-api.onrender.com/api/v1) |
| **Stellar Testnet** | Horizon Network RPC | `https://horizon-testnet.stellar.org` |
| **Stellar Testnet** | Soroban Network RPC | `https://soroban-testnet.stellar.org` |

---

### 💻 Local Development Options

#### Option A — Docker Compose (Full Stack Local Dev)
When running locally via `docker compose up -d --build`, services are live at:
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database:** `localhost:5432`
- **Redis Cache:** `localhost:6379`

#### Option B — Backend Local Dev (Fastest)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DATABASE_URL=sqlite+aiosqlite:///./dev.db CACHE_ENABLED=false uvicorn app.main:app --reload --port 8000
```

#### Option C — Frontend Dashboard
```bash
cd frontend && npm install && npm run dev
```

---

## 📡 REST API Reference

Base URL: `https://stellar-threatnet-api.onrender.com/api/v1` (or `http://localhost:8000/api/v1`)

| Method | Endpoint | Auth Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/lookup/wallet/{address}` | Public | Lookup Stellar wallet reputation (0–100 + category) |
| `GET` | `/lookup/domain/{domain}` | Public | Lookup domain phishing confidence score |
| `GET` | `/lookup/token/{code}/{issuer}` | Public | Lookup token reputation by `CODE:ISSUER` |
| `GET` | `/incidents` | Public | Paginated list of security incidents |
| `POST` | `/incidents` | Analyst+ | Create a new security incident record |
| `GET` | `/threats/latest` | Public | List recently updated non-trusted entities |
| `GET` | `/feed` | Public | Export threat intelligence data in CSV format |
| `GET` | `/stats` | Public | Global threat counts and metrics |
| `GET` | `/stats/overview` | Public | SOC Dashboard summary metrics |
| `GET` | `/search?q={query}` | Public | Multi-entity threat search |
| `POST` | `/reports` | Authenticated | Submit community threat report |
| `POST` | `/reports/{id}/vote` | Authenticated | Upvote / downvote pending report |
| `POST` | `/reports/{id}/moderate` | Moderator+ | Approve (triggers score recompute) or reject |
| `POST` | `/auth/register` | Public | Register new user account |
| `POST` | `/auth/token` | Public | Obtain OAuth2 JWT access token |
| `POST` | `/api-keys` | Authenticated | Generate API key (`X-API-Key`) |

---

## 👥 Community Moderation Workflow

ThreatNet employs a transparent 4-stage moderation workflow:

```
[ Community User ] ──► Submit Report ──► [ Pending Queue ]
                                               │
                                 ┌─────────────┴─────────────┐
                                 ▼                           ▼
                        [ Upvote / Downvote ]       [ Moderator Review ]
                                                     │               │
                                                     ▼               ▼
                                            [ Approve Report ]  [ Reject ]
                                                     │
                                                     ▼
                                          [ Attach Evidence & ]
                                          [ Recompute Score   ]
```

1. **Submission:** Authenticated users submit a report with target type, category, description, and optional evidence URLs.
2. **Peer Review:** Community users upvote or downvote pending reports (one vote per user).
3. **Moderation:** Moderators evaluate evidence. Approving a report attaches verified evidence and **automatically recomputes the target's reputation score**.
4. **Audit Log:** Every decision is written to an immutable append-only audit trail.

---

## 💻 CLI & SDK Usage

### Terminal CLI (`threatnet`)
```bash
cd cli
pip install -e .

# Wallet lookup
threatnet lookup wallet GABC1234...

# Export threat feed
threatnet feed --output feed.csv
```

### Python SDK
```python
from stellar_threatnet_sdk import ThreatNetClient

async with ThreatNetClient(api_key="tn_...") as client:
    wallet = await client.lookup_wallet("GABC1234...")
    print(wallet["status"], wallet["reputation_score"])
```

### TypeScript SDK
```typescript
import { ThreatNetClient } from "@stellar-threatnet/sdk";

const client = new ThreatNetClient({ apiKey: "tn_..." });
const stats = await client.stats();
console.log(stats);
```

---

## 🤝 Contributing

We welcome contributions from security researchers, Rust/Python/TypeScript engineers, and documentation writers!

1. Read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).
2. Check out beginner-friendly issues in [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md).
3. Join community discussions on [GitHub Discussions](https://github.com/smog123/stellar-threatnet-app/discussions).

---

## 📄 License & Credits

Stellar ThreatNet is open-source software released under the [MIT License](LICENSE).

### Related Repositories

* **App (this repo):** [github.com/smog123/stellar-threatnet-app](https://github.com/smog123/stellar-threatnet-app)
* **Contract:** [github.com/smog123/stellar-threatnet-contract](https://github.com/smog123/stellar-threatnet-contract) — Soroban on-chain indicator registry

### Maintainers

| Role | Handle | Contact |
| --- | --- | --- |
| Lead Maintainer | [@smog123](https://github.com/smog123) | [GitHub](https://github.com/smog123) |

### Contributors

[![Contributors](https://contrib.rocks/image?repo=smog123/stellar-threatnet-app)](https://github.com/smog123/stellar-threatnet-app/graphs/contributors)

* **Live Dashboard:** [https://stellar-threatnet.vercel.app](https://stellar-threatnet.vercel.app)
* **Live API Docs:** [https://stellar-threatnet-api.onrender.com/docs](https://stellar-threatnet-api.onrender.com/docs)
