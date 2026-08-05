# Contributing to Stellar ThreatNet

First off — thank you for contributing to the security layer of the Stellar
ecosystem. Every contributor makes wallets, exchanges, and dApps safer.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) and
[Security Policy](SECURITY.md) before contributing.

## How to contribute

1. **Pick an issue**: browse [`GOOD_FIRST_ISSUES.md`](GOOD_FIRST_ISSUES.md) or
   the `good first issue` label. Comment on the issue to claim it.
2. **Fork & branch**: `git checkout -b feat/your-feature` (or `fix/...`).
3. **Make small, focused commits** with clear messages.
4. **Test your change** (see below).
5. **Open a pull request** using the [PR template](.github/pull_request_template.md).

## Development setup

### Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest              # run the full test suite
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### Soroban contract (Rust)

```bash
cd contracts/soroban_threatnet
cargo test
```

### CLI / SDKs

```bash
cd cli && pip install -e .
cd sdks/python && pip install -e .
cd sdks/javascript && npm install
```

## Testing expectations

- **Backend**: every new endpoint needs API tests in `backend/tests/`. Core
  scoring logic needs unit tests. Keep the suite green: `pytest`.
- **Frontend**: run `npm run lint` and `npm run build` before submitting.
- **Contract**: `cargo test` must pass; new state-changing functions need tests.

## Coding conventions

- Python: PEP 8, type hints everywhere, async SQLAlchemy only (no sync queries).
- TypeScript/React: strict mode, functional components, Tailwind utility classes.
- Rust: `cargo fmt` and `cargo clippy` clean; `#![no_std]` in the contract.
- Never commit secrets, `.env` files, or real wallet addresses with balances.
- Prefer small diffs: if your change touches many files, explain why.

## Branch protection & review

- `main` is protected. All changes land via pull request with **one approving
  review** from a maintainer.
- CI must pass (tests, lint, build).
- Security-relevant changes (auth, scoring, moderation, the contract) require
  review by **two** maintainers.

## Community

- GitHub Discussions: feature ideas, governance, and ecosystem questions.
- Issue tracker: bugs and concrete feature requests.

Thank you for making Stellar safer. :star:
