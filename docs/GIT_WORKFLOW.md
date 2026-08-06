# Git Workflow

These are the enforceable and recommended rules for contributing to Stellar
ThreatNet. Local git hooks enforce the commit format and safety checks; the
branch protection rules below must be configured in the GitHub repository
settings (they cannot be committed to the repo).

---

## 1. Setup — install the hooks (once)

```bash
make git-hooks        # sets core.hooksPath to .githooks and chmod +x the hooks
```

This activates two local hooks:

| Hook | Enforces |
| --- | --- |
| `.githooks/commit-msg` | Conventional Commits message format (see §3) |
| `.githooks/pre-commit` | No whitespace errors, no conflict markers, no staged `.env`/key files, no obvious secret material in added lines |

Intentionally bypass (rare, must be justified in the PR): `git commit --no-verify`.

---

## 2. Branching model

Trunk-based development with short-lived branches. `main` is the only long-lived
branch and is always releasable.

| Branch | Purpose | Merges into |
| --- | --- | --- |
| `main` | Protected trunk. Never pushed to directly. | — |
| `feat/<slug>` | New features | `main` |
| `fix/<slug>` | Bug fixes | `main` |
| `security/<slug>` | Security fixes (fast-track, two-reviewer rule) | `main` |
| `docs/<slug>` | Documentation-only changes | `main` |
| `chore/<slug>` | Tooling, deps, CI, refactors | `main` |
| `release/vX.Y.Z` | Release preparation (version bumps, changelog) | `main` + tag |
| `hotfix/vX.Y.Z` | Patch releases from a release branch | `main` + tag |

Rules:

- Branch names are `kebab-case`, ≤ 60 chars, no trailing slashes: `feat/sep-validator-engine`.
- Branches are short-lived — a branch that drifts far from `main` should be rebased, not merged with `main`.
- Keep a branch focused on **one logical change**. If a branch grows multiple concerns, split it.

---

## 3. Commit conventions (enforced locally and in CI)

Format:

```
<type>(<scope>): <subject>
```

| Type | When to use |
| --- | --- |
| `feat` | New user/API-facing capability |
| `fix` | Bug fix |
| `security` | Security hardening / vulnerability fix (two-reviewer rule) |
| `docs` | Documentation only |
| `style` | Formatting, no behaviour change |
| `refactor` | Code change that adds no feature and fixes no bug |
| `perf` | Performance improvement |
| `test` | Adding/fixing tests |
| `build` | Build system, Dockerfile, packaging |
| `ci` | CI workflow changes |
| `deps` | Dependency updates (Dependabot uses this) |
| `chore` | Tooling, maintenance, nothing user-facing |
| `revert` | Reverting a previous change |

Recommended scopes (informational — the hook validates format, not the scope
list): `backend`, `frontend`, `contract`, `sdk`, `sdk-python`, `sdk-js`, `cli`,
`extension`, `seed`, `docs`, `ci`, `deps`.

Rules:

- Imperative mood, lowercase subject: `fix(backend): reject malformed token targets` ✓ (not “Fixed”).
- Subject ≤ 72 characters, no trailing period.
- Breaking changes: add `!` after the type/scope (`feat!: remove v1 lookup endpoints`).
- One logical change per commit; `fixup!`/`squash!` commits are fine locally but must be squashed before merge.
- Merge and `git revert` commits are exempt from the format.
- Body (optional) explains the *why*, not the *what*: reference issues with `Closes #123`.

Example set:

```
feat(backend): add SOC overview endpoint
fix(frontend): make theme toggle persist across pages
security(contract): require auth on admin publish
test(sdk-python): cover token lookup error paths
```

---

## 4. Pull request workflow

1. Branch from an up-to-date `main`.
2. Make focused commits (see §3).
3. Open a PR using the template. **PR title must also follow Conventional Commits** — CI validates it.
4. CI must pass: backend tests, frontend lint/build, contract tests, JS SDK typecheck, CodeQL, commit-message check.
5. Review: **one approving review** for normal changes; **two** for security-relevant changes (auth, scoring, moderation, contract, dependency CVEs).
6. Keep the branch up to date with `main` (rebase or merge `main`). Keep history linear where practical.
7. Squash or rebase before merge — `main` stays linear.

---

## 5. Branch protection (configure in GitHub → Settings → Branches)

These cannot live in the repo; enable them on `main`:

| Setting | Value |
| --- | --- |
| Require a pull request before merging | ✅ (at least 1 approval; 2 for security-relevant) |
| Dismiss stale reviews when new commits are pushed | ✅ |
| Require status checks to pass | ✅ CI, CodeQL |
| Require branches to be up to date before merging | ✅ |
| Require conversation resolution | ✅ |
| Do not allow force pushes | ✅ |
| Do not allow deletions | ✅ |
| Require signed commits (optional) | Recommended once maintainers adopt commit signing |

---

## 6. Releases & hotfixes

1. Cut `release/vX.Y.Z` from `main`; bump versions, update `CHANGELOG.md` and the
   supported-versions table in `SECURITY.md`.
2. Tag `vX.Y.Z` after merge (annotated tag: `git tag -a vX.Y.Z -m "vX.Y.Z"`).
3. Security hotfixes: branch `hotfix/vX.Y.Z` from the release tag, fix, and
   merge to `main` **and** the release branch; tag the patch release.
4. Never rewrite published tags or force-push to protected branches.

---

## 7. Reverting & amending

- Public history (`main`/release branches): always `git revert <sha>` — never rebase/force-push.
- Unpushed local commits: amend freely (`git commit --amend`), then rebase the branch.

---

## 8. Common recipes

```bash
# install hooks
make git-hooks

# fix the message of the last (unpushed) commit
git commit --amend -m "feat(backend): add SOC overview endpoint"

# split one commit into two (unpushed)
git reset -p HEAD~1 && git commit -m "chore: ..." && git commit -m "feat: ..."

# check your staged changes before committing
git diff --cached --stat && git diff --cached --check
```
