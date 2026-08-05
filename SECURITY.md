# Security Policy

Stellar ThreatNet is security infrastructure — its own security posture matters.
We take all vulnerabilities seriously and ask the community to report them
responsibly.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x: (pre-release)  |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email **security@stellar-threatnet.org** with:

1. A description of the vulnerability and its impact.
2. The affected component (backend API, Soroban contract, frontend, CLI, SDK, extension).
3. Steps to reproduce, including any PoC code.
4. Your PGP key (optional) if you want an encrypted response.

### What happens next

1. **Ack (24h)**: A maintainer confirms receipt and opens a private tracking issue.
2. **Triage (72h)**: Severity is assessed and a fix plan is agreed.
3. **Fix & release**: A patch is prepared, reviewed, and released. Public disclosure
   is coordinated **after** a fix is available (or after 90 days for unfixable issues).
4. **Credit**: With your consent, you are credited in the advisory and the release notes.

We operate a **90-day coordinated disclosure** policy: if we cannot provide a fix
within that window, we will publish a partial advisory so the ecosystem can
self-protect.

## Security Guarantees

- Passwords are stored as **bcrypt** hashes only (never plaintext).
- JWTs are signed with a server-side secret; rotate via `SECRET_KEY` in production.
- API keys are stored as **SHA-256 hashes** — plaintext is shown exactly once.
- All score-modifying and moderation actions are append-only **audit logged**.
- Rate limiting (slowapi) protects public endpoints from abuse.
- The Soroban contract stores only cryptographic hashes of indicators, never raw data.

## Dependency & Supply-Chain Security

- Dependabot keeps Python and npm dependencies patched.
- CodeQL SAST runs on every pull request.
- Releases are built from CI with pinned lockfiles.
