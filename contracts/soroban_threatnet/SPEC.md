# Soroban ThreatNet — Contract Specification (v1.0)

Precise specification of the `soroban_threatnet` contract as implemented in
`src/lib.rs` (soroban-sdk **27.0.5**, Rust edition 2021, `#![no_std]`).

This document is the single source of truth for the contract surface. Every
function below maps to a real step in the product flow — there are no
speculative entry points.

---

## 1. Contract identity

| Field | Value |
| --- | --- |
| Package | `soroban_threatnet` |
| Version | `0.1.0` |
| Target | `wasm32v1-none` (Soroban-optimized wasm, Rust 1.82+) |
| Crate type | `cdylib` |
| Purpose | Zero-trust on-ledger registry of SHA-256 threat indicator hashes |

## 2. Storage layout

### 2.1 Instance storage (`env.storage().instance()`)

| DataKey | Type | Written by | Notes |
| --- | --- | --- | --- |
| `DataKey::Admin` | `Address` | `initialize` | Set exactly once. |
| `DataKey::TotalIndicators` | `u32` | `initialize`, `publish_threat_indicator` | Incremented only on first insert of a hash. |

### 2.2 Persistent storage (`env.storage().persistent()`)

| DataKey | Type | Written by | TTL |
| --- | --- | --- | --- |
| `DataKey::Indicator(BytesN<32>)` | `IndicatorRecord` | `publish_threat_indicator` | Default ledger TTL — **not explicitly extended** (see §5 gaps). |

### 2.3 Types

```rust
#[contracttype]
pub enum ThreatLevel {
    Trusted = 0,            // score 80–100
    UnderInvestigation = 1, // score 51–79
    Suspicious = 2,         // score 21–50
    ConfirmedMalicious = 3, // score 0–20
}

#[contracttype]
pub struct IndicatorRecord {
    pub indicator_hash: BytesN<32>, // SHA-256 of the raw indicator
    pub threat_level: ThreatLevel,
    pub reputation_score: u32,      // 0–100, mirrored from the off-chain API
    pub updated_at: u64,            // ledger timestamp of last update
    pub verified_by: Address,       // admin who published
}
```

## 3. Public interface

### 3.1 `initialize(admin: Address) -> ()`

| Aspect | Detail |
| --- | --- |
| Auth | `admin.require_auth()` — the admin address must sign. |
| Panics | `"Already initialized"` if `DataKey::Admin` is already set. |
| Effects | Sets `Admin`, sets `TotalIndicators = 0`. |
| Events | None emitted. |
| Product step | Contract bootstrapping after deploy. Single execution safety. |

### 3.2 `publish_threat_indicator(admin: Address, indicator_hash: BytesN<32>, threat_level: ThreatLevel, reputation_score: u32) -> ()`

| Aspect | Detail |
| --- | --- |
| Auth | `admin.require_auth()` **and** `admin == stored Admin`, else panic `"Unauthorized admin"`. |
| Panics | `"Reputation score must be between 0 and 100"` if `reputation_score > 100`. |
| Effects | Upserts `IndicatorRecord` (hash, level, score, `env.ledger().timestamp()`, admin). Increments `TotalIndicators` only when the hash is new. |
| Events | None emitted. |
| Product step | Backend publishes a moderator-approved indicator onto the ledger. |

### 3.3 `get_threat_indicator(indicator_hash: BytesN<32>) -> Option<IndicatorRecord>`

| Aspect | Detail |
| --- | --- |
| Auth | None (read-only). |
| Returns | `Some(record)` if published, `None` if untracked. |
| Product step | Zero-trust client verification before signing/transacting. |

### 3.4 `get_total_indicators() -> u32`

| Aspect | Detail |
| --- | --- |
| Auth | None (read-only). |
| Returns | Total count of published hashes. |
| Product step | Registry health / metrics. |

## 4. Auth model summary

| Function | `require_auth()` | Additional check |
| --- | --- | --- |
| `initialize` | `admin` | — |
| `publish_threat_indicator` | `admin` | `admin == Admin` |
| `get_threat_indicator` | — | — |
| `get_total_indicators` | — | — |

Admin is a single address. There is no rotation path — changing admin requires a
governance change (deploy a new contract, publish hashes again).

## 5. Known gaps / recommended follow-ups

These are documented, not defects — changing them is out of scope for v1.0.

1. **No events.** Publish/initialize emit nothing. A future `Event` (e.g.
   `(publisher, hash, level, score)`) improves off-chain indexers.
2. **Persistent TTL.** SDK 27 persistent entries rely on the default TTL and are
   never re-extended. Long-lived records need `env.storage().persistent().extend_ttl()`
   or they may expire. Add an `extend_ttl` maintenance call.
3. **No admin rotation** — see §4.
4. **Score/level consistency** is enforced off-chain; on-chain only clamps score
   to `<= 100` (lower bound is enforced by `u32`).

## 6. Deploy & initialize sequence (dependency order)

```bash
# 1. Build
rustup target add wasm32v1-none
cargo build --target wasm32v1-none --release

# 2. Deploy (prints CONTRACT_ID)
soroban contract deploy --wasm target/wasm32v1-none/release/soroban_threatnet.wasm \
  --source <ADMIN_SECRET> --network testnet \
  --rpc-url https://soroban-testnet.stellar.org

# 3. Initialize (must be first invocation)
soroban contract invoke --id <CONTRACT_ID> --source <ADMIN_SECRET> \
  --network testnet -- initialize --admin <ADMIN_ADDRESS>
```

Use `scripts/deploy.sh` for the full sequence with copy-pasteable output.
