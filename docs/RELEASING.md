# Release Process

Cut a tagged release when `main` is stable and CI is green. This is the
checklist used to ship `v0.1.0` and later versions. Branching and tagging rules
live in [GIT_WORKFLOW.md](GIT_WORKFLOW.md) §6.

## 1. Pre-release checklist

- [ ] CI is green on `main` (backend tests, frontend lint/build, JS SDK
      typecheck, CodeQL).
- [ ] Release notes drafted (template below) summarizing user-facing changes.
- [ ] `SECURITY.md` supported-versions table updated to include the new tag.
- [ ] The Soroban contract is deployed (from the contract repo,
      `stellar-threatnet-contract`) and its on-chain addresses captured. If not
      yet deployed, the release notes must say so explicitly — never ship
      placeholder addresses.

## 2. Prepare

1. Cut `release/v0.1.0` from `main`.
2. Bump versions (backend `pyproject.toml`, frontend `package.json`, SDKs, CLI).
3. Update the changelog and the release-notes draft.
4. Merge the release branch, keeping `main` linear (squash or rebase).

## 3. Tag and publish

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0

# optional: GitHub release with notes (requires gh)
gh release create v0.1.0 --title "v0.1.0" --notes-file RELEASE_NOTES_v0.1.0.md
```

## 4. Release notes template (v0.1.0)

### Highlights

- Open-source threat intelligence layer for the Stellar ecosystem: wallet /
  domain / token reputation lookups, incident database, community moderation,
  AI assistant, SDKs, CLI, and browser extension.
- Live dashboard and API; on-chain indicator registry (Soroban, deployed from
  the `stellar-threatnet-contract` repo).

### Deployed on-chain registry

| Network | Contract address |
| --- | --- |
| Testnet | `C...` — fill after `soroban contract deploy` |
| Mainnet | `C...` — fill after mainnet deployment |

Post-deploy initialization (admin only, once):

```bash
soroban contract invoke --id <contract-id> -- initialize --admin <admin G...>
```

### Changelog highlights

- ... (list user-facing changes since the previous tag)

## 5. Post-release

- Update the Wave submission materials in `docs/wave/` with the tag and
  contract verification links.
- Announce the release in GitHub Discussions.
