# feat(backend): dispute and appeal workflow with trusted-org fast-track

## Summary

Let flagged entities appeal a low reputation score with supporting evidence, and
give trusted organizations a fast-track review path through the moderator queue.

## Why it matters

False positives are the main risk of any threat-intelligence system. A formal,
audit-logged appeal path keeps the dataset fair and keeps legitimate projects
from being harmed.

## Acceptance Criteria

- [ ] Appeal model with reason, evidence URLs, and status
- [ ] `POST /appeals` (authenticated) and moderator review endpoints
- [ ] Trusted-org appeals are marked for fast-track review
- [ ] Every appeal decision is append-only audit logged
- [ ] Approved appeals trigger score recomputation
- [ ] Tests cover the full appeal lifecycle

## Tech Stack

Python 3.11 · FastAPI · SQLAlchemy 2.0 · Celery · pytest
