# Status — SymbiOS Ω-GATE + PoSE-Lite MVP

- Branch: `cassandra/omega-pose-mvp`
- Scope: runnable FastAPI skeleton with Ω-GATE scoring and PoSE-Lite evidence capture
- Evidence sink: `symbios/evidence.json` (JSON array) and `symbios/pose_log.txt` (NDJSON envelopes)
- Bench: `python symbios/scripts/bench_full.py` (requires FastAPI app running at `localhost:8000`)

## Outstanding
- Harden policy/coverage heuristics and add unit tests
- Wire signatures for envelope `E.signature`
- Package dependencies (FastAPI, Uvicorn, requests) in requirements file
