# Architecture & System Design Specification

## 1. Executive Summary

Stellar ThreatNet provides open-source, high-performance threat intelligence infrastructure specifically engineered for the Stellar network ecosystem. The architecture balances real-time threat querying (<20ms response time via Redis caching) with robust relational integrity (PostgreSQL database) and decentralized immutability (Soroban Rust smart contracts).

---

## 2. System Architecture Diagram

```
[ Clients: Wallets / Explorers / dApps / Extension ]
                     │
                     ▼
[ NGINX Reverse Proxy / Cloudflare WAF ]
                     │
                     ▼
[ FastAPI Service Instances (Python 3.11) ]
       │             │             │
       ├─────────────┼─────────────┤
       ▼             ▼             ▼
[ PostgreSQL ]  [ Redis Cache ]  [ Celery Workers ]
(ThreatDB)      (Lookup Cache)   (Background Processing,
                                  Stellar Horizon Ingestion)
                                   │
                                   ▼
                         [ Soroban Smart Contract ]
                         (On-chain Threat Hashes)
```

---

## 3. Component Breakdown

### 3.1 Backend API Service (FastAPI)
- **Framework**: FastAPI (Asynchronous Python 3.11 with `uvicorn`/`gunicorn`).
- **ORM**: SQLAlchemy 2.0 with `asyncpg` driver for non-blocking PostgreSQL queries.
- **Authentication**: JWT tokens (ECDSA/RS256) with OAuth2 Password Flow. Role-Based Access Control (`admin`, `analyst`, `moderator`, `reporter`, `read_only`).
- **Security**: Rate limiting via `slowapi` / Redis fixed-window counters; CORS origin restrictions; SQL Injection & XSS sanitization filters.

### 3.2 Database Tier (PostgreSQL + Redis)
- **PostgreSQL 15**: Primary datastore for normalized entities (Wallets, Domains, Tokens, Incidents, Reports, Evidence, Audit Logs, API Keys).
- **Redis 7**: High-performance key-value caching layer for endpoint lookups (`threatnet:wallet:<address>`, `threatnet:domain:<domain>`) and Celery message broker.

### 3.3 Asynchronous Task Worker Tier (Celery)
- **Celery Worker**: Evaluates community report consensus, auto-recalculates reputation scores upon new evidence ingestion, and periodically polls Stellar Horizon endpoints to detect suspicious multi-account creation loops or clawbacks.

### 3.4 Soroban Smart Contract (`SorobanThreatNet`)
- **Language**: Rust (`soroban-sdk`).
- **Purpose**: Stores cryptographically verified threat indicators (SHA-256 hashes of blacklisted Stellar addresses and malicious domain names) directly on the Stellar testnet/mainnet ledger for zero-trust client verification.

### 3.5 AI Threat Assistant Service
- **Engine**: Modular LLM adapter interface (supporting OpenAI, Anthropic, or local Ollama instances) with structured fallback prompting.
- **Guardrails**: Strict prompt template enforcing factual evidence referencing without speculating or claiming 100% certainty on unverified threats.

---

## 4. Scalability & Resilience Strategy

1. **Read-Heavy Optimization**: 95%+ of queries are lookup checks. Caching layer serves requests directly from Redis with a 15-minute TTL, falling back to PostgreSQL indexed queries.
2. **Horizontal Scaling**: Backend containers are stateless, allowing auto-scaling behind load balancers.
3. **Database Indexing**: B-tree indexes on `address`, `domain_name`, `asset_code`, `issuer_address`, `created_at`, and `reputation_score`.

---

## 5. Security & Threat Vector Controls

| Threat Vector | Mitigation Strategy |
|---|---|
| API Abuse / DDoS | Redis-backed sliding-window rate limiting per IP and API key. |
| Spam Reports | Reputation staking / required authentication + moderation consensus workflow. |
| Data Corruption | Append-only audit logs for all score modifications and admin actions. |
| False Positives | Dispute resolution workflow with fast-track trusted organization appeals. |
