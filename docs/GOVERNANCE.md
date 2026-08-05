# Governance Model

ThreatNet is ecosystem infrastructure: who decides what is flagged as
"malicious" is a trust question. This document defines how the project and its
data are governed.

## Principles

1. **Transparency** — every reputation score has an explainable evidence trail
   and an audit log entry.
2. **Due process** — every flagged entity can be disputed and appealed.
3. **Openness** — the dataset, code, and moderation rules are public.
4. **Conservatism** — the cost of a false positive (blocked wallet) is treated
   as seriously as a false negative (missed scam).

## Project governance

- **Maintainers**: responsible for merge decisions, releases, and CI. Decisions
  are made by lazy consensus; contentious changes go to GitHub Discussions.
- **Two-review rule**: auth, scoring, moderation, and contract changes require
  two maintainer reviews.
- **TNIPs (ThreatNet Improvement Proposals)**: structural changes (scoring
  formula changes, new data types, governance changes) are proposed as TNIPs,
  discussed for at least 7 days, then voted on by maintainers.

## Data governance (the reputation database)

### Roles

| Role | Can |
| --- | --- |
| Reporter | submit reports, vote |
| Moderator | approve/reject reports, update incidents |
| Analyst | publish verified incidents |
| Admin | manage users, read audit logs |

### Evidence levels (confidence)

1. Community report — 0.3
2. Multi-source correlation — 0.6
3. Analyst verified — 0.9
4. On-chain / contract proof — 1.0

### Moderation rules

- Reports must be approved by a moderator before affecting reputation.
- A report is rejected if it is a duplicate, lacks evidence, or targets an
  entity already under review with contradicting evidence.
- Moderators must leave a moderation note on rejection.

### Disputes & appeals

1. A flagged entity's operator submits a dispute (with evidence of legitimacy).
2. The dispute is reviewed by **two** moderators/analysts.
3. Approved disputes remove evidence and recompute the score; the process is
  audit-logged end to end.
4. Fast-track: verified ecosystem organizations (e.g. anchors) may appeal
  through a dedicated channel with a 24-hour SLA.

## Funding & neutrality

ThreatNet must remain neutral. Paid API tiers (if introduced) buy capacity,
not moderation outcomes. All moderation and admin decisions are logged and
publicly inspectable to enforce this.
