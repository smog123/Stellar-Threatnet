# Stellar Threat Intelligence Data & Scoring Model

## 1. Reputation Scoring Matrix

Reputation scores range from **0 (Maximum Threat / Confirmed Malicious)** to **100 (Fully Trusted / Verified Entity)**.

| Score Range | Category | Action Recommendation for Wallets/dApps |
|---|---|---|
| **0 - 20** | `CONFIRMED_MALICIOUS` | **BLOCK**: Explicit warning, auto-reject transaction or domain access. |
| **21 - 50** | `SUSPICIOUS` | **WARN**: Show prominent warning prompt to user before proceeding. |
| **51 - 79** | `UNDER_INVESTIGATION` | **INFO**: Display informational note; unverified reports present. |
| **80 - 100** | `TRUSTED` | **ALLOW**: Verified legitimate entity (e.g. known exchange anchor). |

---

## 2. Dynamic Scoring Formula

The reputation score $S$ for an entity $E$ is calculated dynamically as:

$$S(E) = \text{BaseScore}(E) - \sum_{i=1}^{N} (W_i \times C_i) + B_{verified}$$

Where:
- $\text{BaseScore}(E) = 80$ (default initial score for newly observed entities)
- $W_i$: Weight of evidence item $i$ — set by its **proof type**, per `EVIDENCE_WEIGHTS` in `backend/app/services/threat_engine.py`:

  | Proof type | Weight | Typical use |
  | --- | ---: | --- |
  | `onchain_proof` | 50 | On-ledger trace, contract audit finding, automated forensic proof |
  | `payload_sample` | 40 | Captured phishing payload (fake SDK script, memo text, asset memo) |
  | `tx_hash` | 30 | A specific transaction demonstrating the behavior |
  | `domain_screenshot` | 25 | Screenshot of a claim/phishing landing page |
  | `multi_source` | 20 | Several independent sources or brand-protection feeds |
  | `other` | 15 | Anything that does not fit the types above |
- $C_i$: Confidence level of evidence $i$ ($0.0 \le C_i \le 1.0$)
- $B_{verified}$: Boost bonus (+20) for verified Stellar Ecosystem Anchors / KYB verified organizations.

---

## 3. Entity Classification Types

### 3.1 Wallet Categories
- `MALICIOUS_DRAINER`: Automated account balance drainer scripts.
- `PHISHING_RECEIVER`: Destination address receiving funds from phishing campaigns.
- `RANSOMWARE`: Destination address associated with extortion or ransomware.
- `EXPLOIT_EXECUTOR`: Address executing Soroban contract reentrancy or logic exploits.
- `SUSPICIOUS_SPAMMER`: Address broadcasting mass low-value memos/claimable balances.

### 3.2 Domain Categories
- `FAKE_WALLET`: Phishing site impersonating Freighter, Lobstr, xBull, or Albedo.
- `FAKE_EXCHANGE`: Fake interface mimicking StellarTerm, StellarX, or centralized exchanges.
- `FAKE_AIRDROP`: Malicious site requiring key signature for fake token distribution.
- `MALICIOUS_SOROBAN_DAPP`: Impersonating dApp frontends interacting with malicious contracts.

### 3.3 Token / Asset Categories
- `IMPERSONATION`: Token duplicating ticker/logo of established assets (e.g. fake `USDC` or `XLM`).
- `SCAM_RUGPULL`: Asset minted with malicious clawback/freeze abuse or liquidity withdrawal.
- `ABANDONED`: Defunct token issuer key locked without activity for >3 years.

---

## 4. Evidence Integrity & Verification Levels

1. **Level 1 (Community Report)**: Unverified submission by authenticated user (Confidence: 0.3).
2. **Level 2 (Multi-Source Correlation)**: Multiple independent community reports (Confidence: 0.6).
3. **Level 3 (Analyst Verified)**: Security analyst manually verified evidence log / transaction hash (Confidence: 0.9).
4. **Level 4 (Automated Forensic Proof)**: On-chain cryptographic proof / Soroban contract audit finding (Confidence: 1.0).

---

## 5. Worked Examples

These match the implementation in `backend/app/services/threat_engine.py`
(`compute_score`): start at 80, subtract `weight × confidence` per evidence
item, add 20 if verified, clamp to [0, 100], round, then band by status:

| Rounded score | Status | Integrator action |
| --- | --- | --- |
| 0–20 | `confirmed_malicious` | BLOCK |
| 21–50 | `suspicious` | WARN |
| 51–79 | `under_investigation` | INFO badge |
| 80–100 | `trusted` | ALLOW |

### Example A — Wallet drainer (score 3, confirmed malicious)

A wallet receives funds from a Staking-Marathon claim scam. An analyst
attaches two approved evidence items:

- `onchain_proof`, confidence 1.0 (Level 4 — on-ledger trace): −50
- `tx_hash`, confidence 0.9 (Level 3 — analyst verified): −27

```
S = 80 − (50 × 1.0) − (30 × 0.9) = 80 − 50 − 27 = 3
```

Score 3 → `confirmed_malicious` → **BLOCK** the address.

### Example B — Phishing domain (score 46, suspicious)

A claim landing page for a memo-phishing wave, e.g. `getxlm.org`:

- `domain_screenshot`, confidence 0.9 (Level 3): −22.5
- `multi_source`, confidence 0.6 (Level 2 — two independent reports): −12

```
S = 80 − (25 × 0.9) − (20 × 0.6) = 80 − 22.5 − 12 = 45.5 → 46 (rounded)
```

Score 46 → `suspicious` → **WARN** users before they visit.

### Example C — Token impersonation, then verified boost (44 → 64)

A token mimics `USDC` with an unauthorized issuer:

- `payload_sample`, confidence 0.9 (Level 3): −36

```
S = 80 − (40 × 0.9) = 44 → suspicious → WARN
```

The issuer later completes ecosystem-anchor verification (+20):

```
S = 80 − 36 + 20 = 64 → under_investigation → INFO badge
```

The boost rewards verified issuers but cannot alone turn a confirmed drainer
into a trusted anchor — evidence still dominates below 80.

### Sanity check from the test suite

The moderation test (`backend/tests/test_reports.py`) asserts exactly one
`tx_hash` evidence at confidence 1.0:

```
S = 80 − (30 × 1.0) = 50 → suspicious, reputation_score == 50
```

### A note on seeded demo data

The dashboard seed (`backend/scripts/seed.py`) stores scores and statuses
directly for demo purposes; the evidence records attached to seeded entities
are illustrative and do not necessarily reproduce those stored values through
the formula. Only recomputed values (from an approved report) are guaranteed
to follow the formula above.
