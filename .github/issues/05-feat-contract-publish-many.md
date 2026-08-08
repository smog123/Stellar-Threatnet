# feat(contract): batch publish indicators with publish_many

## Summary

Add `publish_many(admin: Address, hashes: Vec<BytesN<32>>, levels: Vec<u32>,
scores: Vec<u32>)` to `contracts/soroban_threatnet/src/lib.rs` for batched
on-chain indicator updates behind a single auth check.

## Why it matters

Bulk backfills and bulk re-scoring currently require one `publish_threat_indicator`
call per indicator, which is slow and expensive on-ledger. Batching reduces
calls and keeps updates atomic.

## Acceptance Criteria

- [ ] `publish_many` performs a single `require_auth(admin)` for the whole batch
- [ ] Input vectors are length-checked; mismatched lengths fail cleanly
- [ ] All hashes in the batch are stored on success
- [ ] Unit tests cover happy path, length mismatch, and unauthorized callers
- [ ] `cargo fmt` and `cargo clippy` are clean

## Tech Stack

Rust · soroban-sdk 27 · `#![no_std]` · soroban testutils
