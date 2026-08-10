# feat(contract): emit Soroban events on indicator publish

## Summary

Emit Soroban contract events from `publish_threat_indicator` (and
`publish_many`) so indexers and off-chain monitors can react to on-chain
updates without polling storage.

## Why it matters

Event emission is the standard Soroban integration surface. It lets the
backend, explorers, and third-party monitors build live feeds on top of the
registry.

## Acceptance Criteria

- [ ] A `publish` event carries the indicator hash (and level/score) as topics or data
- [ ] `publish_many` emits one event per indicator (or one batch event — state the choice)
- [ ] Tests assert event emission with expected topics
- [ ] The contract repo `README.md` documents the event schema

## Tech Stack

Rust · soroban-sdk 27 events · soroban testutils
