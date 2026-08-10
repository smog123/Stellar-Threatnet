#!/usr/bin/env bash
# ============================================================ #
# Configure branch protection on a Stellar ThreatNet repo.     #
#                                                              #
# The CI job names are used as required status checks — fetch   #
# the real workflow files and keep the list in sync.           #
#                                                              #
# Usage (requires a PAT with admin:repo — GITHUB_TOKEN from    #
# Actions does not have admin scope):                          #
#                                                              #
#   gh auth login --with-token < pat.txt                       #
#   ./scripts/set_branch_protection.sh smog123/stellar-threatnet-app \
#     "Backend (pytest),Frontend (build),JavaScript SDK (typecheck),Conventional Commits,CodeQL"
#   ./scripts/set_branch_protection.sh smog123/stellar-threatnet-contract \
#     "Soroban contract (cargo test + wasm),Conventional Commits,CodeQL"
# ============================================================ #
set -euo pipefail

REPO="${1:?Usage: $0 owner/repo \"Check 1,Check 2\"}"
CHECKS="${2:-}"

# The API requires `contexts` to be an array of plain check-run name
# strings (not objects) — see branch-protection REST schema.
checks_json="[]"
if [ -n "$CHECKS" ]; then
  checks_json='['
  IFS=',' read -ra NAMES <<< "$CHECKS"
  for name in "${NAMES[@]}"; do
    checks_json+="\"${name}\","
  done
  checks_json="${checks_json%,}]"
fi

echo "==> Enabling branch protection on ${REPO}/main"
echo "    required status checks: ${CHECKS:-<none>}"

gh api --method PUT "repos/${REPO}/branches/main/protection" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": $checks_json
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "==> Branch protection is now active on ${REPO}/main"
echo "    (force pushes are blocked — use PRs for all changes)"
