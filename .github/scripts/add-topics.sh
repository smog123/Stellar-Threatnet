#!/usr/bin/env bash
#
# Add discoverability topics to the GitHub repository. Requires gh + auth.
#
# Usage: .github/scripts/add-topics.sh [owner/repo]
set -euo pipefail

REPO="${1:-smog123/stellar-threatnet-app}"

if ! command -v gh >/dev/null 2>&1; then
  echo "error: gh CLI is required — install from https://cli.github.com" >&2
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "error: gh is not authenticated — run 'gh auth login' first" >&2
  exit 1
fi

# Contract repos get Rust/Soroban-flavored topics; the app repo gets the
# full application-oriented set.
if [[ "$REPO" == *-contract ]]; then
  topics=(stellar soroban threat-intelligence blockchain-security phishing-protection security rust web3)
else
  topics=(stellar soroban threat-intelligence blockchain-security phishing-protection osint cybersecurity security fastapi web3)
fi

args=()
for t in "${topics[@]}"; do args+=(--add-topic "$t"); done
gh repo edit "$REPO" "${args[@]}"

echo "topics added to ${REPO}."
