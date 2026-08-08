# Drips Wave for Stellar — Submission Pack

Status: **ready for the submission steps — verified live 2026-08-08**.
Only user-side actions remain (record the demo video below; run the
in-app submission flow at https://www.drips.network/app).

---

## 1. Live status check (Phase 1 + 12.1)

- **Approved list:** Stellar ThreatNet is **not** on the
  [Drips Wave for Stellar approved repos](https://www.drips.network/wave/stellar/repos)
  list — re-verified 2026-08-08: **667 repos approved, zero matches for
  ThreatNet / threatnet**. Submission is open.
- **Landscape:** approved repos cluster around escrow (Trustless Work,
  SafeTrust, KindFi), RWA (akkuea, StellarRent), and freelance marketplaces
  (OFFER-HUB). There is no shared security / threat-intelligence layer in the
  approved set — **that is this project's white space.**
- **SDF priorities:** Soroban adoption and ecosystem tooling, DeFi, developer
  infrastructure, and smart-contract security (Soroban Audit Bank) — all
  aligned with a security-infrastructure project.
- **Real-world scale of the problem:**
  - CertiK *Hack3d: Web3 Security Report 2024*: phishing was the most costly
    attack vector, ~**$1.05B lost across 296 incidents** (~44% of the $2.36B
    total on-chain losses that year).
  - SlowMist *2024 Blockchain Security & AML Annual Report*: wallet-drainer
    attacks ~**$494M in direct losses**, up **67% YoY**, ~332,000 addresses hit.

## 2. Project description (submission form, one paragraph)

> Stellar ThreatNet is an open-source, community-driven threat-intelligence
> layer for the Stellar ecosystem. Phishing remains Web3's most costly attack
> vector — $1.05B lost in 2024 (CertiK) — and Stellar has no shared
> infrastructure to warn users before they sign a malicious transaction. The
> platform collects, validates, and scores reputation data for Stellar wallet
> addresses, domains, and tokens; serves it through a low-latency REST API used
> by wallets, exchanges, dApps, and a Manifest V3 browser extension; and anchors
> SHA-256 hashes of confirmed indicators on the Stellar ledger through a
> Soroban contract, so verification never depends on trusting the API itself.
> Evidence-backed scores (0–100) are recomputed from community reports and
> moderator-approved evidence, and every moderation decision is audit-logged.

## 3. Repo relationship description

> The project is intentionally split into two repositories, each independently
> eligible for the program. **stellar-threatnet-contract** is a pure Rust
> Soroban workspace — one contract, `soroban_threatnet`, that stores SHA-256
> hashes of confirmed threat indicators with an admin-gated publish path.
> **stellar-threatnet-app** is the application monorepo: a FastAPI backend
> (REST + Celery + Horizon ledger monitoring), a Next.js SOC dashboard, Python
> and TypeScript SDKs, a CLI, and a browser extension. The two connect through
> a single contract interface (`SPEC.md`): the backend publishes
> moderator-approved indicator hashes; clients verify them on-chain directly,
> independent of the API.

## 4. Planned issues (grounded in the issues created by `scripts/create_issues.sh`)

Planned work is organized by area and already tracked as real issues in both
repositories:

- **Contract (`stellar-threatnet-contract`):** emit lifecycle events, add
  persistent-TTL extension (records currently rely on default TTL), admin
  rotation, score-boundary tests, and publishing verified on-chain addresses.
- **Backend (`stellar-threatnet-app`):** admin bulk-publish endpoint to sync
  the on-chain registry, ingestor edge-case tests.
- **Frontend:** zero-trust on-chain verification badge on the wallet page,
  client-side lookup caching.
- **SDK / CLI:** on-chain verification helpers in both SDKs and a
  `threatnet verify` command.
- **Extension:** token (`CODE:ISSUER`) reputation badges.
- **Docs:** worked scoring examples for the threat model.

Run `./scripts/create_issues.sh --app <owner>/stellar-threatnet-app` and
`--contract <owner>/stellar-threatnet-contract` to (re)generate the batch.

## 5. Supporting links checklist (gather before submitting)

- [x] Live app: https://frontend-rosy-five-50.vercel.app (HTTP 200, verified 2026-08-08)
- [x] Live API docs: https://stellar-threatnet-api.onrender.com/docs (HTTP 200)
- [x] Live API health: https://stellar-threatnet-api.onrender.com/health (HTTP 200, `{"status":"ok"}`)
- [x] App repo: https://github.com/smog123/stellar-threatnet-app (HTTP 200, v0.1.0 release)
- [x] Contract repo: https://github.com/smog123/stellar-threatnet-contract (HTTP 200, v0.1.0 release)
- [x] On-chain contract verification links (block explorer): **testnet deployed 2026-08-08**
      — `CB34YG3ZGQ3FGK32D6GMMFKKK4SPWN5QURF4VCCQ67ZHBILJBH2KBCG5`
      (https://stellar.expert/explorer/testnet/contract/CB34YG3ZGQ3FGK32D6GMMFKKK4SPWN5QURF4VCCQ67ZHBILJBH2KBCG5),
      initialized and read-verified. Mainnet deployment pending.
- [x] Documentation site: docs/ pages are the primary docs (the docs/ tree in
      stellar-threatnet-app); a GitBook mirror is optional (Phase 11).
- [ ] **Demo video (required):** record the 60–90s walkthrough following
      `DEMO_VIDEO_SCRIPT.md` (shot list with real URLs, seeded addresses, and
      voiceover). Script is ready; recording is the last remaining user action.

## 6. How to submit (verified 2026-08-08 — user-side actions)

The Stellar Wave application is an **in-app onboarding flow**, not an email or
form. Steps (per Drips docs, `docs.drips.network/wave`):

1. Sign in to **https://www.drips.network/app** with the GitHub account that
   owns the repos (`smog123`).
2. Navigate to **Maintainers → Orgs and Repos**.
3. Install the **Drips Wave GitHub App** on the `smog123` account (personal
   account — installs directly; no org needed). Grant access to both repos:
   `stellar-threatnet-app` and `stellar-threatnet-contract`.
4. Sync repositories, then **apply both** to the **Stellar Wave Program**.
   Submit them separately — each is independently eligible (the playbook's
   two-repo split maximizes surface area).
5. Wait for program-organizer approval (in-app + email notification). If
   declined, appeal via **Maintainers → Orgs and Repos → Appeal** (appeals by
   email are ignored).

Notes:
- The platform evaluates public code, issue health, and activity — it does not
  ask for a demo video or a written form. The demo video is still worth
  recording: it is the single artifact that proves the product works end to
  end and it is referenced in every conversation with reviewers.
- Wave cycles run monthly (e.g. Wave 7 was Jul 23–30, $75k budget). If no
  wave is active at submission time, apply anyway so the repos are approved
  and ready for the next cycle; subscribe to the Drips newsletter + Discord
  for the schedule.
- The 13 planned issues (8 app #29–36, 5 contract #3–7) are the planned-work
  signal for the "planned issues" description and give contributors scoped
  entry points.

## 7. Post-approval iteration policy (Phase 13)

Treat every new gap the same way:

1. **Scope it honestly** — quick addition or core-architecture change? Say so
   before writing the issue.
2. **Cross-repo dependencies** — if a change spans both repos, file coordinated
   issues with an explicit "Depends on: <repo>#<issue>" cross-reference.
3. **Write with the same rigor** — Summary, why it matters, scoped options for
   design decisions, Acceptance Criteria, Tech Stack.
4. **Never build out of order** — a frontend feature that depends on a contract
   change ships only after the contract is deployed. Sequencing mistakes create
   bugs that look like regressions.
