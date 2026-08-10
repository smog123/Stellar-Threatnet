# test(contract): publish-to-get round-trip integration test

## Summary

Exercise the full `publish_threat_indicator` → `get_threat_indicator`
round-trip against a local Soroban sandbox as a CI job, in addition to the
existing unit tests.

## Why it matters

The current unit tests validate the workflow with test snapshots. A sandbox
round-trip catches integration issues (storage, TTL, auth) that unit tests can
miss.

## Acceptance Criteria

- [ ] Test invokes publish then get for the same hash and asserts the stored values
- [ ] Test runs in a CI job (e.g. `cargo test` with a sandbox-backed runner)
- [ ] Test snapshot files are updated where applicable
- [ ] Failing auth (non-admin publish) is asserted in the same flow

## Tech Stack

Rust · soroban-sdk testutils · GitHub Actions
