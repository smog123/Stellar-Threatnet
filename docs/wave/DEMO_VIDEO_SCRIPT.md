# Demo Video — Shot List (60–90s, single take)

**Purpose:** Phase 12 submission artifact. Shows the full product flow end to end:
lookup → report → moderate → score recompute → on-chain verification.

**Recording setup:** Screen-record at 1080p, browser at ~125% zoom, light or dark
theme (dark recommended — matches the dashboard). No mouse-cursor recording
needed, but keep the pointer visible and deliberate. Record with a 2–3s pause
after every click. If you fumble a step, pause 2s, redo it, and cut the pause in
editing — do not restart the whole take.

**Vocal pacing:** one sentence per action, no rushing. The voiceover below is
exactly ~75s at a natural pace. Keep it plain — no buzzwords, no "seamlessly".

---

## Shot 0 — Title card (0:00–0:04, optional)
Black frame or browser home with the repo banner.
> VO: "Stellar ThreatNet — open-source threat intelligence for the Stellar ecosystem."

## Shot 1 — Dashboard (0:04–0:15)
Open **https://frontend-rosy-five-50.vercel.app**
- Pause on the SOC header + network banner.
- Hover (do not click) over the counters: malicious wallets, phishing domains,
  pending reports, active campaigns.
- Hover the "Latest threat intelligence" list and the "Activity feed".

> VO: "The Security Operations Center gives a live posture read on the Stellar
> ecosystem — flagged wallets, phishing domains, scam tokens, active campaigns,
> and the community moderation queue, all in one screen."

## Shot 2 — Lookup a flagged wallet (0:15–0:28)
Click **Reputation Lookup** in the nav (or go to `/lookup`). Wallet tab is default.
Paste:
```
GNMWIORQUELDWMRNXJWILPW3XIPJBST5DMGCZCCWJHFIG27UF7AOQAAA
```
Press enter / submit. Pause on the result: **score gauge at 12**, red
`confirmed_malicious` badge, category "Drainer", assessment text, report count.

> VO: "Look up any wallet, domain, or token. This address scores 12 out of 100 —
> flagged as a confirmed drainer with evidence-backed community reports behind
> the score."

## Shot 3 — Lookup a trusted entity (0:28–0:36, contrast beat)
Back to `/lookup`, paste:
```
GSPCJ42ZLHJJDDOKYJGGDO5FZXYPSHMENZMNJJXOQ5QDVZQARLIAQAAA
```
Pause on the green `trusted` badge and high score.

> VO: "Compare against a verified ecosystem anchor: high score, trusted badge.
> Scores are recomputed from evidence — never hardcoded."

## Shot 4 — Submit a report (0:36–0:50)
Go to **Community** (`/community`). Fill the "Submit a threat report" form:
- Target type: **domain**
- Target value: `claim-xlm-rewards.xyz` (or any string — it's a new report)
- Suggested category: `Fake Airdrop`
- Description: `Landing page in a new claim-XLM memo-phishing wave. Harvests secret keys via a fake wallet-connect flow.`
- Evidence URL: `https://stellar.expert/tx/demo` (optional field — leave blank if unsure)
- Open the "Authenticated?" details box, paste the **reporter demo token**
  (register/obtain beforehand: `POST /api/v1/auth/register` or use the seeded
  `reporter@stellar-threatnet.org` / `threatnet-demo` account)
- Click **Submit report**. Pause on the green confirmation: "Report REP-… queued
  for moderation (status: pending)."

> VO: "Anyone can report a suspicious wallet, domain, or token. The report
> doesn't touch any scores yet — it's queued for moderation, so one person can't
> move reputation alone."

## Shot 5 — Moderate it (0:50–1:05)
Open **https://stellar-threatnet-api.onrender.com/docs** in a new tab (or
`/docs` locally). This is the honest path: moderation is an API, and the demo
shows the live queue + approval.
1. `GET /reports/queue` → **Try it out** → Execute. Show the pending report you
   just submitted at the top of the JSON list.
2. `POST /reports/{id}/moderate` → set `action: "approve"`, a short
   `moderation_note` (e.g. `Confirmed via live page + wallet-connect check`),
   paste the report id → Execute. Show the `"status": "approved"` response.

> VO: "A moderator reviews the queue and approves with an evidence note.
> Every decision is audit-logged — moderation is append-only."

## Shot 6 — Score recompute (1:05–1:18)
Back to the app. If the domain you reported is new, the lookup returns
"no reputation data" → then re-run **Community** → open the report → show
`approved` status. For the recompute beat, look up the wallet from Shot 2 again
(or a domain from the seeded set, e.g. `xn--stellr-mta.com`) and show its score
has updated relative to the earlier view / the feed timestamp has refreshed.

> VO: "Once approved, the indicator flows into lookups and the intelligence feed
> — the score you saw in the lookup now reflects the approved report."

## Shot 7 — On-chain verification (1:18–1:30)
Open the deployed contract on testnet:
```
https://stellar.expert/explorer/testnet/contract/CB34YG3ZGQ3FGK32D6GMMFKKK4SPWN5QURF4VCCQ67ZHBILJBH2KBCG5
```
Pause on the contract page. Optionally show the `initialize` transaction via
stellar.expert search, or run a read against the RPC in the terminal:

> VO: "The registry itself lives on-chain: a Soroban contract on Stellar
> testnet that stores SHA-256 hashes of confirmed indicators, so verification
> never depends on trusting our API."

**Honesty note (do not skip):** indicator *publishing* to the contract is a
planned feature (`publish_threat_indicator` is in the contract; the backend
admin-publish endpoint is a planned issue). The demo therefore shows the *live
deployed contract* and its read path — do not claim hashes are already being
written. If you want a fuller beat, run `get_total_indicators` against the
deployed contract in the terminal during this shot.

## Shot 8 — Close (1:30–1:40)
Back to the dashboard, fade out.
> VO: "Open source, community-moderated, and verifiable on-chain. Stellar
> ThreatNet — stellar-threatnet-app and stellar-threatnet-contract."

---

## Pre-flight checklist (before recording)
- [ ] `POST /api/v1/auth/register` a reporter + moderator account, or confirm
      the seeded demo users exist on the deployed backend
- [ ] Have the reporter token copied (paste-ready, it's masked input)
- [ ] Confirm a moderator can reach `GET /reports/queue` (needs MODERATOR/ADMIN role)
- [ ] Load every URL above once in advance so nothing is cold at record time
- [ ] Disable notifications / tab noise; close unused tabs
- [ ] Record in one continuous take; pause 2s before each click

## Fallbacks
- If the queue shows nothing, submit Shot 4's report *before* starting the
  recording, then start recording at Shot 1 (or pick Shot 5 up after it).
- If `stellar.expert` is slow, screenshot the contract page and hold it 3s as a
  static beat — never skip the on-chain shot entirely.
- If the deployed backend rejects the report (auth), fix auth first, then
  record — do not improvise around a 401 on camera.
