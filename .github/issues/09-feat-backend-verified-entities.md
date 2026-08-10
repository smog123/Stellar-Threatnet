# feat(backend): verified-entity program with on-chain verification

## Summary

Allow trusted ecosystem anchors and organizations to verify entities. A
verification is audit-logged and applies the verified boost to the reputation
score formula (the `+20` term in the scoring model).

## Why it matters

Official entities (anchors, well-known dApps) should be distinguishable from
impersonators. Verification is the trust anchor for the entire scoring model.

## Acceptance Criteria

- [ ] Admin endpoint to grant/revoke verified status on an entity
- [ ] Verification event is written to the append-only audit log
- [ ] Score recomputation applies the verified boost
- [ ] Optionally support on-chain verification proof (Soroban)
- [ ] Tests cover grant, revoke, and score effects
- [ ] `docs/GOVERNANCE.md` and `docs/THREAT_MODEL.md` updated

## Tech Stack

Python 3.11 · FastAPI · SQLAlchemy 2.0 · Celery · pytest
