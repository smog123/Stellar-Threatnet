# test: wire coverage report into CI with a badge

## Summary

Run `pytest --cov` as part of CI, enforce a coverage threshold, and surface the
result with a coverage badge in the README.

## Why it matters

Threat-intelligence code paths (scoring, moderation, auth) deserve measured
coverage. A CI-enforced threshold turns coverage from a report into a guarantee.

## Acceptance Criteria

- [ ] `pytest --cov=app` runs in the CI test job
- [ ] A failing threshold (e.g. 80%) fails the job — value documented in the workflow
- [ ] Coverage summary is uploaded/available as a CI artifact
- [ ] README gains a coverage badge
- [ ] `pytest-cov` is pinned in `backend/requirements.txt`

## Tech Stack

pytest-cov · GitHub Actions · README badges
