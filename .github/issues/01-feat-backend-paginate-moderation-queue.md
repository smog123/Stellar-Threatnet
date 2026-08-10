# feat(backend): paginate the community moderation queue

## Summary

`GET /reports/queue` currently returns up to 50 pending reports with no
pagination. Add `limit`/`offset` query parameters consistent with `GET
/incidents`, and return a way for clients to know the total count.

## Why it matters

The moderation queue grows with community reports. Moderators need to page
through the queue, and API clients need stable, documented paging semantics.

## Acceptance Criteria

- [ ] `GET /reports/queue` accepts `limit` (default 50, max 200) and `offset`
- [ ] Response includes the total number of pending reports
- [ ] Existing behavior is preserved when the new parameters are omitted
- [ ] Unit tests cover paging, default values, and max-limit clamping
- [ ] `docs/API.md` documents the new parameters

## Tech Stack

Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) · pytest
