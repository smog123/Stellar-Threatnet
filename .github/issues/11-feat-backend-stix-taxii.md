# feat(backend): STIX/TAXII export and MISP integration

## Summary

Export confirmed indicators as STIX 2.1 bundles (and optionally expose a TAXII
collection), plus a Celery job to publish the indicator set to a MISP feed.

## Why it matters

Threat intel is only as good as its distribution. Interoperating with STIX/TAXII
and MISP puts Stellar-specific indicators into the tooling security teams
already run.

## Acceptance Criteria

- [ ] `GET /feed/stix` returns a STIX 2.1 bundle of confirmed indicators
- [ ] Content negotiation and pagination behave like the CSV feed
- [ ] Optional TAXII collection endpoint is documented
- [ ] MISP publishing job runs via Celery with configured auth
- [ ] Tests cover bundle generation for empty and populated datasets
- [ ] `docs/API.md` documents the new endpoints

## Tech Stack

Python 3.11 · stix2 library · FastAPI · Celery · pytest
