#!/usr/bin/env bash
# ============================================================ #
# Create every planned issue for a Stellar ThreatNet repo in   #
# one run (Phase 10 — issue generation at scale).              #
#                                                              #
# Usage:                                                       #
#   ./scripts/create_issues.sh --app smog123/stellar-threatnet-app
#   ./scripts/create_issues.sh --contract smog123/stellar-threatnet-contract
#                                                              #
# Requires: gh CLI, authenticated with issues:write scope.     #
# Issues are idempotent by title: if one exists, it is         #
# skipped.                                                     #
# ============================================================ #
set -euo pipefail

: "${GH:=gh}"

usage() {
  echo "Usage: $0 --app REPO | --contract REPO" >&2
  exit 1
}

# $1 = repo, $2 = title, $3 = body, $4 = labels (comma-separated)
create_issue() {
  local repo="$1" title="$2" body="$3" labels="$4"
  if "$GH" issue list --repo "$repo" --search "in:title \"${title}\"" --state all --json number --jq 'length' | grep -q '^[1-9]'; then
    echo "skip (exists): ${title}"
    return 0
  fi
  if [ -n "${DRY_RUN:-}" ]; then
    echo "would create: ${title} [${labels}]"
    return 0
  fi
  "$GH" issue create --repo "$repo" --title "$title" --body "$body" --label "$labels" \
    >/dev/null
  echo "created: ${title}"
}

# ---------------- App repo issues ----------------
app_issues() {
  local repo="$1"

  create_issue "$repo" \
    "feat(frontend): add zero-trust on-chain indicator check panel" \
    "## Summary
The wallet page should verify a reputation verdict against the Soroban contract directly, not only via the REST API.

## Why it matters
Zero-trust verification is a core product promise. Users should be able to confirm an on-ledger record without trusting our API.

## Acceptance Criteria
- [ ] `frontend/src/lib/contract.ts` implements `readIndicator(hashHex)` via `@stellar/stellar-sdk` (see docs/wave/APP_AGENT_SYSTEM_PROMPT.md §7)
- [ ] Wallet page shows an on-chain verification badge (verified / not found) when `THREATNET_CONTRACT_ID` is set
- [ ] Hash is computed client-side with SHA-256 (Web Crypto); no raw identifiers sent to the contract
- [ ] Missing env vars degrade gracefully (badge hidden, no console spam)
- [ ] Typecheck + lint pass

## Tech Stack
TypeScript, Next.js 14, @stellar/stellar-sdk, Web Crypto" \
    "enhancement, good first issue"

  create_issue "$repo" \
    "feat(backend): add admin bulk-publish endpoint for indicator hashes" \
    "## Summary
Add an admin-only endpoint that publishes a batch of confirmed indicator hashes to the Soroban contract.

## Why it matters
Moderators approve threats in the API; the on-chain registry must stay in sync. Manual per-hash publishing does not scale.

## Acceptance Criteria
- [ ] `POST /admin/contract/publish` (admin role only, audit-logged)
- [ ] Accepts a JSON array of `{sha256, threat_level, reputation_score}` (max 50 per call)
- [ ] Each hash is upserted to the contract via the admin key; partial failures are reported per-hash
- [ ] Response contains per-hash status and the final `get_total_indicators()` count
- [ ] API tests cover auth (403 for non-admin) and validation

## Tech Stack
Python 3.11, FastAPI, SQLAlchemy 2.0, httpx, @stellar/stellar-sdk (server-side)" \
    "enhancement, backend"

  create_issue "$repo" \
    "feat(sdk): add contract read helpers to Python and JS SDKs" \
    "## Summary
Expose `verify_indicator(hash_hex)` on both SDKs so downstream users can do zero-trust checks in two lines.

## Why it matters
SDKs are the primary integration surface; on-chain verification belongs in them.

## Acceptance Criteria
- [ ] Python: `ThreatNetClient.verify_indicator(hash_hex) -> IndicatorRecord | None`
- [ ] JavaScript: `client.verifyIndicator(hashHex) -> IndicatorRecord | null`
- [ ] Both accept raw identifiers (address/domain/token) and hash internally
- [ ] Unit tests with a mocked RPC server; documented in both READMEs

## Tech Stack
Python (httpx), TypeScript (ESM), @stellar/stellar-sdk" \
    "enhancement, sdk"

  create_issue "$repo" \
    "perf(frontend): add request caching to lookup pages" \
    "## Summary
Cache lookup responses client-side (SWR or equivalent) to cut redundant API calls and improve perceived latency.

## Why it matters
The SOC dashboard and extension both hit lookups repeatedly; 15-minute server cache exists, client cache is missing.

## Acceptance Criteria
- [ ] Lookup pages reuse cached data within a 5-minute window
- [ ] Cache is per-entity key; invalidation on explicit refresh
- [ ] No regressions in a11y or dark/light theme

## Tech Stack
TypeScript, Next.js 14, SWR" \
    "enhancement, frontend, good first issue"

  create_issue "$repo" \
    "feat(cli): add threatnet verify command" \
    "## Summary
Add `threatnet verify <wallet|domain|token> <value>` that prints the API verdict and the on-chain verification result side by side.

## Why it matters
Security researchers need a scriptable way to verify indicators.

## Acceptance Criteria
- [ ] Command resolves the entity, hashes it, queries the contract
- [ ] Prints verdict, score, and on-chain status in one table
- [ ] `--json` output for scripting; exit code 1 for confirmed_malicious

## Tech Stack
Python, click, httpx, @stellar/stellar-sdk" \
    "enhancement, cli"

  create_issue "$repo" \
    "docs: add threat model worked examples" \
    "## Summary
Add three fully worked scoring examples (phishing domain, wallet drainer, token impersonation) to docs/THREAT_MODEL.md with real numbers.

## Why it matters
docs/THREAT_MODEL.md explains the formula; worked examples prove it end to end and help reviewers.

## Acceptance Criteria
- [ ] Three examples with step-by-step weight/confidence arithmetic
- [ ] Each ends in a verdict range and recommended action
- [ ] Formulas match the implementation in `backend/app/services/threat_engine.py`

## Tech Stack
Markdown" \
    "documentation"

  create_issue "$repo" \
    "test(backend): extend ingestor tests for Horizon stream edge cases" \
    "## Summary
Add tests for the live Horizon ingestor: malformed memos, rapid-transfer detection limits, and network timeouts.

## Why it matters
The ingestor streams production ledger data; silent failures erode trust in threat feeds.

## Acceptance Criteria
- [ ] Malformed/unparseable operations are skipped, not fatal
- [ ] Timeout path falls back cleanly (no leaked tasks)
- [ ] Coverage added to `backend/tests/test_ingestor.py`

## Tech Stack
Python 3.11, pytest, httpx (mocked)" \
    "test, backend"

  create_issue "$repo" \
    "feat(extension): add token reputation badge to asset pages" \
    "## Summary
Extend the browser extension to look up `CODE:ISSUER` tokens and show a reputation badge on known asset pages.

## Why it matters
Token impersonation is one of the highest-volume scams on Stellar; the extension currently only checks domains.

## Acceptance Criteria
- [ ] Content script extracts `CODE:ISSUER` patterns from the page
- [ ] Badge shows verdict + score; confirmed_malicious shows the blocking banner
- [ ] Cache per token for 15 minutes (matches domain behavior)

## Tech Stack
JavaScript, Manifest V3, DOM observers" \
    "enhancement, extension"
}

# ---------------- Contract repo issues ----------------
contract_issues() {
  local repo="$1"

  create_issue "$repo" \
    "feat(contract): emit events on initialize and publish" \
    "## Summary
Emit `Event` payloads from `initialize` and `publish_threat_indicator` so off-chain indexers can observe changes.

## Why it matters
SPEC.md §5 lists missing events as the top gap; indexers currently poll.

## Acceptance Criteria
- [ ] `initialize` emits `(topic: [\"initialize\"], admin)`
- [ ] `publish_threat_indicator` emits `(topic: [\"publish\"], publisher, hash, level, score)`
- [ ] Tests assert emitted events (topics + data)
- [ ] SPEC.md and AGENT_SYSTEM_PROMPT.md updated in the same commit

## Tech Stack
Rust, soroban-sdk 27.0.5" \
    "enhancement, contract"

  create_issue "$repo" \
    "feat(contract): add persistent TTL extension maintenance call" \
    "## Summary
Add a maintenance function that extends the TTL of persistent indicator records before expiry.

## Why it matters
SPEC.md §5 flags that persistent entries are never re-extended; long-lived records could expire and vanish from the registry.

## Acceptance Criteria
- [ ] `extend_ttl(hash: BytesN<32>, extend_to: u64)` callable by admin
- [ ] Extends both the record and, if present, the contract instance
- [ ] Test verifies `env.storage().persistent().get_ledger_key` TTL increases
- [ ] Documented in SPEC.md

## Tech Stack
Rust, soroban-sdk 27.0.5" \
    "enhancement, contract, security"

  create_issue "$repo" \
    "feat(contract): add admin rotation function" \
    "## Summary
Add `set_admin(new_admin: Address)` gated by the current admin to allow key rotation without redeploying.

## Why it matters
SPEC.md §4 documents no rotation path; single-key admin is an operational risk.

## Acceptance Criteria
- [ ] `set_admin` requires current admin auth; emits event
- [ ] Old admin can no longer publish after rotation
- [ ] Rotation is rejected if the new address equals the old
- [ ] Tests cover both auth paths

## Tech Stack
Rust, soroban-sdk 27.0.5" \
    "enhancement, contract"

  create_issue "$repo" \
    "test(contract): add score boundary tests" \
    "## Summary
Add tests for reputation_score boundaries: 0, 100, 101 (must panic), and level/score consistency.

## Why it matters
The score is a security signal; boundary behavior must be locked down.

## Acceptance Criteria
- [ ] `publish_threat_indicator` with score 101 panics with the documented message
- [ ] Score 0 and 100 accepted and round-trip
- [ ] Coverage noted in SPEC.md

## Tech Stack
Rust, soroban-sdk 27.0.5 (testutils)" \
    "test, contract"

  create_issue "$repo" \
    "chore: publish verified contract addresses" \
    "## Summary
Publish the deployed contract IDs (testnet/mainnet) and verification links in README.md and the v0.1.0 release notes.

## Why it matters
Reviewers and integrators need canonical on-chain addresses to verify.

## Acceptance Criteria
- [ ] Testnet + mainnet CONTRACT_IDs listed with block-explorer links
- [ ] Admin rotation plan documented (per the set_admin issue)
- [ ] Release notes reference the addresses

## Tech Stack
Markdown, Stellar block explorer" \
    "chore, documentation"
}

case "${1:-}" in
  --app)      [ -n "${2:-}" ] && app_issues "$2" || usage ;;
  --contract) [ -n "${2:-}" ] && contract_issues "$2" || usage ;;
  *) usage ;;
esac
