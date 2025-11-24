from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_PATH = BASE_DIR / "evidence.json"
LOCAL_LOG = BASE_DIR / "pose_log.txt"


def canonical_serialize(data: Dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def register_evidence(s: Dict[str, Any], gate_result: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": s.get("model"),
        "input": s.get("input", {}),
        "output": s.get("output", {}),
        "context": s.get("context", {}),
        "omega_gate": gate_result,
    }

    evidence_hash = hashlib.sha256(canonical_serialize(entry)).hexdigest()

    envelope = {
        "id": entry["id"],
        "hash": evidence_hash,
        "signature": None,
        "timestamp": entry["timestamp"],
    }

    existing_evidence: list[Dict[str, Any]] = []
    if LOG_PATH.exists():
        try:
            existing_evidence = json.loads(LOG_PATH.read_text(encoding="utf-8"))
            if not isinstance(existing_evidence, list):
                existing_evidence = []
        except json.JSONDecodeError:
            existing_evidence = []

    existing_evidence.append({"D": entry, "H": evidence_hash, "E": envelope})
    LOG_PATH.write_text(json.dumps(existing_evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with LOCAL_LOG.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(envelope, ensure_ascii=False) + "\n")
