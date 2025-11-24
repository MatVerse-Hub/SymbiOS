# Roadmap: SymbiOS Ω-GATE + PoSE-Lite MVP

## Milestone 1 — MVP (this branch)
- FastAPI endpoint `/symbios/ia/invoke` with Ω-GATE scoring
- PoSE-Lite evidence capture to `evidence.json` and `pose_log.txt`
- Benchmark script `scripts/bench_full.py` for local smoke testing

## Milestone 2 — Hardening
- Expand policy filters and add configurable thresholds
- Add structured error handling and observability (metrics + logging)
- Provide OpenAPI examples and contract tests

## Milestone 3 — Attestation
- Implement signing pipeline for envelopes (`E.signature`)
- Add provenance metadata (model version, dataset fingerprints)
- Integrate with remote verifier for replay/verification

## Milestone 4 — Production
- Containerize service and publish Helm chart
- CI pipeline with linting, type-checking, and load tests
- Blue/green deploy hooks with rollback criteria
