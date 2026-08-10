# feat(backend): add new threat categories (FAKE_EXCHANGE)

## Summary

Extend the threat category set in `backend/app/models/entities.py` and the
schemas with new categories such as `FAKE_EXCHANGE` and `CLONE_APP`, and add
corresponding seed data and tests.

## Why it matters

The taxonomy must reflect the actual attack surface of the Stellar ecosystem.
New categories let moderators classify reports precisely, which feeds the
scoring engine and the dashboard filters.

## Acceptance Criteria

- [ ] New category values are added to the model enum and Pydantic schemas
- [ ] Lookup and search responses display the new categories
- [ ] Seed data includes at least one entity per new category
- [ ] Unit tests cover serialization and validation of the new values
- [ ] Migration (Alembic) is included if the schema changes

## Tech Stack

Python 3.11 · FastAPI · SQLAlchemy 2.0 · Alembic · pytest
