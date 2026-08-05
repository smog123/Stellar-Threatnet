# Stellar ThreatNet — Browser Extension

Manifest V3 extension that warns users before they interact with known
Stellar phishing websites (fake wallets, fake exchanges, fake airdrops).

## Install (development)

1. Open `chrome://extensions` (Chrome/Edge) or `about:debugging` (Firefox).
2. Enable **Developer mode**.
3. Click **Load unpacked** and select this `browser-extension/` directory.

## How it works

- The content script asks the background service worker to check the current
  hostname against the ThreatNet API (`GET /lookup/domain/{host}`).
- `confirmed_malicious` → blocking banner with a "Leave this site" action.
- `suspicious` → amber warning banner.
- Results are cached locally for 15 minutes.
- Untracked domains are cached as neutral and never block.

## Configuration

The API base URL is `https://api.stellar-threatnet.org/api/v1` by default.
For local development against a local backend, change `API_BASE` in
`src/background.js` (and add the host to `host_permissions` in
`manifest.json`).

## Safety note

ThreatNet blocks domains **only** after moderator-approved evidence. An
untracked domain is *unknown*, not safe — always verify URLs independently.
