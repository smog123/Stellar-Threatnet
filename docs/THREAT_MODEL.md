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
- $W_i$: Weight of threat indicator $i$ (e.g., Phishing Link = 40, Rugpull asset = 50, Spam = 15)
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
