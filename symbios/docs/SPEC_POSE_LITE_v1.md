# PoSE-Lite Specification (v1)

PoSE-Lite records approved Ω-GATE events as evidence for downstream verification and replay.

## Workflow
1. Ω-GATE approves a request and passes the full payload plus decision summary.
2. PoSE-Lite canonicalizes the data and computes a SHA-256 hash.
3. Evidence is appended to `evidence.json` and a compact log line is written to `pose_log.txt`.

## Evidence envelope
- **D**: full decision record `{ id, timestamp, model, input, output, context, omega_gate }`
- **H**: SHA-256 hash over `D`
- **E**: envelope `{ id, hash, signature, timestamp }`

## Files
- `evidence.json`: JSON array with all evidence entries (human-readable)
- `pose_log.txt`: newline-delimited envelopes for lightweight downstream ingestion

## Hashing
- Canonical JSON serialization with sorted keys and compact separators to ensure deterministic hashes.

## Extensibility
- `signature` field is reserved for future signing and attestation mechanisms.
