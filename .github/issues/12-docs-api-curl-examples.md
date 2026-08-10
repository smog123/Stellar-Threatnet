# docs(api): add curl examples for every endpoint

## Summary

`docs/API.md` documents every endpoint but lacks runnable examples. Add a `curl`
example with a sample request and response for each endpoint, and link the
endpoints from the README API table.

## Why it matters

Working examples are the fastest way for integrators and security researchers
to start using the API without guessing at payload shapes.

## Acceptance Criteria

- [ ] Every endpoint in `docs/API.md` has a `curl` example
- [ ] Sample request and response bodies are shown for POST/PATCH endpoints
- [ ] README API table links to the corresponding `docs/API.md` section
- [ ] Examples use placeholder values (no real addresses or keys)

## Tech Stack

Markdown · curl
