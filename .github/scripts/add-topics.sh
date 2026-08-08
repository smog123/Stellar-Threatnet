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

gh repo edit "$REPO" \
  --add-topic stellar \
  --add-topic soroban \
  --add-topic threat-intelligence \
  --add-topic blockchain-security \
  --add-topic phishing-protection \
  --add-topic osint \
  --add-topic cybersecurity \
  --add-topic security \
  --add-topic fastapi \
  --add-topic web3

echo "topics added to ${REPO}."
