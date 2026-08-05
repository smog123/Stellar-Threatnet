# Stellar ThreatNet Roadmap

> Vision: become the trusted open-source security intelligence layer for the
> Stellar ecosystem — the shared threat database that wallets, explorers,
> exchanges, dApps, and researchers all integrate with.

Legend: ✅ shipped · 🚧 in progress · 🔜 planned

## Phase 1 — Core Infrastructure (current)

- ✅ Backend API (FastAPI + PostgreSQL + Redis + Celery)
- ✅ Wallet / domain / token reputation lookups
- ✅ Incident database with pagination & filtering
- ✅ Community reports with moderation queue (multi-reviewer votes)
- ✅ JWT authentication, RBAC, API keys, append-only audit logs
- ✅ Threat feed (CSV download), latest threats, statistics, search
- ✅ AI threat assistant (mock provider + provider adapter interface)
- ✅ Soroban on-chain threat hash contract
- ✅ Test suite, Docker Compose, CI, security docs

## Phase 2 — Distribution & Integrations

- 🚧 Official Python + TypeScript SDKs with examples
- 🚧 Developer CLI (`threatnet lookup|submit|feed|stats`)
- 🚧 Next.js dashboard (lookups, incidents, moderation, docs)
- 🚧 Browser extension (Manifest V3) phishing warnings
- 🔜 Real AI provider wiring (OpenAI / Anthropic / Ollama) with guardrails
- 🔜 Horizon-based automated monitoring (multi-account creation, clawback abuse)

## Phase 3 — Ecosystem Trust

- 🔜 Verified-entity program (ecosystem anchors, KYB) with on-chain verification
- 🔜 Dispute & appeal workflow with fast-track trusted-organization appeals
- 🔜 Threat indicator sharing protocols (STIX/TAXII export, MISP integration)
- 🔜 Public status page and data-quality metrics

## Phase 4 — Scale & Governance

- 🔜 Multi-tenant quotas and SLA-backed API plans
- 🔜 Decentralized moderation (reputation-staked voting)
- 🔜 Formal governance model for the indicator database (see docs/GOVERNANCE.md)
- 🔜 ThreatNet Improvement Proposals (TNIPs)

## Non-goals (deliberately)

ThreatNet is **not** a wallet, an explorer, an antivirus, or a legal oracle.
We build reusable security infrastructure only.
