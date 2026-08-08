<div align="center">

<img src="assets/banner.svg" alt="Stellar ThreatNet — Open Threat Intelligence for the Stellar Ecosystem" width="100%">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI Pipeline](https://github.com/smog123/Stellar-Threatnet/actions/workflows/ci.yml/badge.svg)](https://github.com/smog123/Stellar-Threatnet/actions)
[![CodeQL Security Audit](https://github.com/smog123/Stellar-Threatnet/actions/workflows/codeql.yml/badge.svg)](https://github.com/smog123/Stellar-Threatnet/actions)
[![Backend Tests](https://img.shields.io/badge/tests-45%20passing-brightgreen.svg)](backend/tests/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Community](https://img.shields.io/badge/Community-Discussions-8b5cf6.svg)](https://github.com/smog123/Stellar-Threatnet/discussions)

# 🛡️ Stellar ThreatNet

> **Open-Source Shared Security & Threat Intelligence Infrastructure for the Stellar Ecosystem.**

[Live Dashboard](https://frontend-rosy-five-50.vercel.app) · [Live API Docs](https://stellar-threatnet-api.onrender.com/docs) · [GitHub Repository](https://github.com/smog123/Stellar-Threatnet)

</div>

---

## 📌 Executive Summary

**Stellar ThreatNet** is the first open-source, decentralized threat intelligence platform built specifically for the **Stellar blockchain ecosystem**.

In Web3 security, malicious actors frequently deploy credential-harvesting phishing domains, automated wallet drainers, fake airdrop tokens, and scam DEX liquidity pools. **ThreatNet solves this by serving as the underlying security intelligence layer** — collecting, validating, scoring, and distributing reputation data on malicious Stellar wallet addresses, domains, and tokens.

> 💡 **What ThreatNet Is and Is Not:**
> - **IS:** The security intelligence layer underneath Web3 applications (wallets, exchanges, dApps, block explorers, browser extensions, and security researchers).
> - **IS NOT:** A crypto wallet, a blockchain explorer, or an antivirus application.

---

## 📖 Table of Contents

- [Executive Summary](#-executive-summary)
- [Why Stellar ThreatNet?](#-why-stellar-threatnet)
- [System Architecture](#-system-architecture)
- [Core Platform Modules](#-core-platform-modules)
- [Reputation Scoring Engine](#-reputation-scoring-engine)
- [Soroban Smart Contract (On-Chain Registry)](#-soroban-smart-contract-on-chain-registry)
- [Repository Structure](#-repository-structure)
- [Quick Start Guide](#-quick-start-guide)
  - [Prerequisites](#prerequisites)
  - [Option A — Docker Compose (Full Stack)](#option-a--docker-compose-full-stack)
  - [Option B — Backend Local Dev (Fastest)](#option-b--backend-local-dev-fastest)
  - [Option C — Frontend Dashboard](#option-c--frontend-dashboard)
- [REST API Reference](#-rest-api-reference)
- [Community Moderation Workflow](#-community-moderation-workflow)
- [CLI & SDK Usage](#-cli--sdk-usage)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Security & Responsible Disclosure](#-security--responsible-disclosure)
- [Contributing & Community](#-contributing--community)
- [License & Credits](#-license--credits)

---

## 🎯 Why Stellar ThreatNet?

Blockchains are immutable and pseudonymized by design. When a user sends funds to a malicious wallet or enters their seed phrase into a fake dApp portal, transactions cannot be reversed.

Existing security solutions are often proprietary, siloed, or lack specialized context for Stellar constructs (such as `G...` public keys, Stellar asset codes `CODE:ISSUER`, SEP compliance standards, and Soroban smart contracts).

**ThreatNet bridges this gap by providing:**
1. **Real-time Explainable Reputation Scores (0–100):** Every wallet, domain, and token gets a score derived from verified evidence.
2. **Open REST API & Feeds:** Wallets and dApps can query APIs in <10ms to warn users *before* they sign dangerous transactions.
3. **On-Chain Zero-Trust Registry:** Confirmed indicator SHA-256 hashes are anchored directly on the Stellar ledger via Soroban smart contracts.
4. **Community-Driven Moderation:** Security researchers submit reports; moderators verify evidence and trigger score re-evaluations.

---

## 🚀 System Architecture

ThreatNet uses a decoupled microservices architecture designed for high throughput, low latency, and operational resilience:

```
                            ┌───────────────────────────┐
                            │   Community & Analysts    │
                            └─────────────┬─────────────┘
                                          │
                                          ▼
  ┌───────────────────┐     ┌───────────────────────────┐     ┌───────────────────┐
  │ Browser Extension │ ──► │  Next.js 14 Dashboard /   │ ──► │ CLI & SDKs        │
  │ (Manifest V3)     │     │  Frontend (Tailwind CSS)  │     │ (Python / JS)     │
  └───────────────────┘     └─────────────┬─────────────┘     └───────────────────┘
                                          │
                                          ▼
                            ┌───────────────────────────┐
                            │     FastAPI Backend       │
                            │ (JWT + API keys, RBAC)    │
                            └─────────────┬─────────────┘
                                          │
               ┌──────────────────────────┼──────────────────────────┐
               ▼                          ▼                          ▼
    ┌───────────────────┐      ┌────────────────────┐      ┌───────────────────┐
    │ PostgreSQL 15     │      │ Redis 7 / Celery   │      │ Soroban Contract  │
    │ (SQLAlchemy 2.0)  │      │ (Cache & Workers)  │      │ (Stellar Ledger)  │
    └───────────────────┘      └────────────────────┘      └───────────────────┘
```

### **Architecture Highlights**
- **Frontend Dashboard (Next.js 14 / TypeScript / Tailwind):** Production-grade SOC interface supporting both Light Mode (default) and Dark Mode.
- **Async Backend API (FastAPI / Python 3.11+):** Asynchronous REST API utilizing SQLAlchemy 2.0, slowapi rate limiting, JWT authentication, and RBAC.
- **Relational Store (PostgreSQL 15):** Normalized storage for indicators, incidents, audit logs, user credentials, and moderation votes.
- **Cache & Async Task Queue (Redis 7 + Celery):** 15-minute lookup caching with fallback and background score recalculation.
- **Soroban Smart Contract (Rust / Soroban SDK 27):** Immutable on-chain registry storing indicator SHA-256 hashes.

---

## 🔍 How ThreatNet Detects Threats on Stellar

ThreatNet uses a combination of **automated Stellar ledger monitoring**, **algorithmic heuristics**, and **cryptographic proof verification**:

### 1. **Stellar Horizon Ledger Watcher (On-Chain Automation)**
- 📩 **Memo Phishing & Dust Spammers:** Scans live Stellar ledger payments for 0.0000001 XLM transfers carrying malicious URL text in `MEMO_TEXT` / `MEMO_MEMO` fields.
- 💸 **Automated Wallet Drainers:** Monitors rapid sequential funds transfers from newly created accounts to central destination keys (`G...`).
- 🪙 **Asset Impersonation (`CODE:ISSUER`):** Audits newly created assets where asset codes match major tokens (e.g. `USDC`, `BTC`) but the `ISSUER` key does not match official ecosystem anchors.

### 2. **Soroban Smart Contract & Web Surface Analysis**
- 📜 **Soroban Host Function Scans:** Analyzes `InvokeHostFunction` calls for dangerous authorization scopes and reentrancy vectors.
- 🌐 **Homograph & Typosquatting Scanning:** Automatically fuzzy-matches newly registered web domains against official Stellar URLs (`stellar.org`, `lobstr.co`, `freighter.app`).
- 🔒 **On-Chain Indicator Hashes:** Stores confirmed indicator SHA-256 hashes in ThreatNet's Soroban Rust contract for zero-trust client lookups.

---

## 🧩 Core Platform Modules

| Module | Description | Primary Use Case |
| :--- | :--- | :--- |
| **Wallet Reputation Engine** | Real-time score (0–100) and verdict (`confirmed_malicious`, `suspicious`, `under_investigation`, `trusted`) for Stellar `G...` keys. | Wallet signature warning before transaction submission. |
| **Domain Reputation System** | Detects fake Stellar portals, spoofed DEX claim sites, and homograph phishing domains. | Phishing protection in browser extension & dApp connects. |
| **Token Reputation Index** | Tracks Stellar assets (`CODE:ISSUER`), identifying impersonation and spam tokens. | Filtering asset lists on DEX interfaces & explorers. |
| **Incident Intelligence Database** | Timeline of major Stellar ecosystem security events with severity and mitigations. | Ecosystem security monitoring and SOC awareness. |
| **Community Moderation Queue** | Upvote/downvote and moderator workflow for crowdsourced threat submissions. | Decentralized evidence validation and scoring inputs. |
| **Soroban On-Chain Registry** | Rust contract storing SHA-256 indicator hashes on Stellar Mainnet/Testnet. | Zero-trust verification without relying on REST APIs. |
| **Browser Phishing Protection** | Manifest V3 Chrome/Brave extension providing instant domain warnings. | Direct end-user protection against fake websites. |

---

## 🧮 Reputation Scoring Engine

Reputation scores range from **0 to 100**, where **0 is confirmed malicious** and **100 is fully trusted**.

### **Verdict Ranges**

| Score Range | Status | Recommended Action |
| :--- | :--- | :--- |
| **0 – 20** | `confirmed_malicious` | **BLOCK** transaction / warning banner |
| **21 – 50** | `suspicious` | **WARN** user to verify details |
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

The Soroban smart contract allows zero-trust clients to verify indicator hashes directly on the Stellar ledger. It lives in its own repository — **`stellar-threatnet-contract`** (Rust, soroban-sdk 27, wasm target `wasm32v1-none`) — and is tracked here via the interface in [`docs/wave/APP_AGENT_SYSTEM_PROMPT.md`](docs/wave/APP_AGENT_SYSTEM_PROMPT.md). The authoritative spec is [`SPEC.md`](https://github.com/smog123/stellar-threatnet-contract/blob/main/SPEC.md).

### **Contract Methods**
- `initialize(admin: Address)` — Sets the admin authority (single execution safety).
- `publish_threat_indicator(admin: Address, hash: BytesN<32>, level: u32, score: u32)` — Admin-gated publication of indicator hash.
- `get_threat_indicator(hash: BytesN<32>) -> Option<Indicator>` — On-chain lookup.
- `get_total_indicators() -> u32` — Returns total indicators registered on-chain.

> 🔒 **Privacy Guarantee:** Raw wallet addresses or domain names are never stored on the public blockchain — only cryptographic SHA-256 hashes are recorded.

---

## 📁 Repository Structure

This is the **application repository** (`stellar-threatnet-app`). The Soroban
contract lives in its own repository: [`stellar-threatnet-contract`](https://github.com/smog123/stellar-threatnet-contract).

```
stellar-threatnet-app/
├── backend/                 # FastAPI service (Python 3.11+, async SQLAlchemy, Celery)
│   ├── app/api/v1/          # REST API endpoints (auth, lookups, incidents, reports, stats)
│   ├── app/core/            # Config, security, JWT, rate limiting
│   ├── app/models/          # SQLAlchemy relational models
│   ├── app/schemas/         # Pydantic schemas
│   ├── app/services/        # Threat scoring engine, cache, tasks
│   └── tests/               # Pytest suite (45 unit & integration tests)
├── frontend/                # Next.js 14 dashboard (TypeScript, Tailwind CSS)
├── cli/                     # Official `threatnet` terminal CLI tool
├── sdks/                    # Client SDKs
│   ├── python/              # Python SDK
│   └── javascript/          # TypeScript / JavaScript SDK
├── browser-extension/       # Manifest V3 Chrome extension
├── docs/                    # Deep-dive documentation (Architecture, Threat Model, API, wave/)
├── scripts/                 # Repo tooling (issue generation, branch protection)
├── assets/                  # Logos and branding SVGs
├── render.yaml              # 1-Click Render cloud deployment blueprint
├── docker-compose.yml       # Production Docker Compose orchestration
└── Makefile                 # Build & test task runner
```

---

## 📋 Quick Start Guide

### Prerequisites
- **Python:** 3.11 or higher
- **Node.js:** 18 or higher
- **Docker & Docker Compose** (optional for containerized deployment)
- **Rust & Cargo** (optional for smart contract development)

---

### Option A — Docker Compose (Full Stack)

To spin up the entire application stack (PostgreSQL, Redis, FastAPI Backend, Celery Worker, Next.js Dashboard):

```bash
# 1. Clone repository
git clone https://github.com/smog123/Stellar-Threatnet.git
cd Stellar-Threatnet

# 2. Copy environment file and configure secrets
cp .env.example .env

# 3. Build and launch containers
docker compose up -d --build
```

**Services will be live at:**
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database:** `localhost:5432`
- **Redis Cache:** `localhost:6379`

---

### Option B — Backend Local Dev (Fastest)

For API development without Docker:

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend in zero-config dev mode (SQLite + local memory)
DATABASE_URL=sqlite+aiosqlite:///./dev.db CACHE_ENABLED=false uvicorn app.main:app --reload --port 8000
```

---

### Option C — Frontend Dashboard

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
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

## ✅ Testing & Quality Assurance

ThreatNet maintains strict automated test coverage across all subsystems:

```bash
# Backend Pytest Suite (45 unit/integration tests)
cd backend && .venv/bin/python -m pytest -q

# Soroban Smart Contract Tests (3 Rust unit tests + Wasm build)
cd contracts/soroban_threatnet
cargo test
cargo build --target wasm32v1-none --release

# Frontend Type Check & ESLint
cd frontend
npm run lint
npx tsc --noEmit
```

---

## 🛡️ Security & Responsible Disclosure

ThreatNet takes security seriously. If you discover a vulnerability within ThreatNet infrastructure:
- **Do NOT create a public issue.**
- Email details directly to **`security@stellar-threatnet.org`**.
- We adhere to a standard **90-day coordinated vulnerability disclosure policy**.

### **Built-In Security Safeguards**
- Passwords hashed using `bcrypt`.
- API Keys stored strictly as cryptographic SHA-256 hashes.
- Production environment enforces strong `SECRET_KEY` requirements ($\ge 32$ bytes).
- Full append-only audit log tracking all moderation and administrative actions.

---

## 🤝 Contributing & Community

We welcome contributions from security researchers, Rust/Python/TypeScript engineers, and documentation writers!

1. Read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).
2. Check out beginner-friendly issues in [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md).
3. Join community discussions on [GitHub Discussions](https://github.com/smog123/Stellar-Threatnet/discussions).

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

* **Live Dashboard:** [https://frontend-rosy-five-50.vercel.app](https://frontend-rosy-five-50.vercel.app)
* **Live API Docs:** [https://stellar-threatnet-api.onrender.com/docs](https://stellar-threatnet-api.onrender.com/docs)
