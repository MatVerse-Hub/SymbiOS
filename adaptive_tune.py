from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from antifragile_config import load_config, save_config

LOG_PATH = Path("antifragile_log.jsonl")


def _read_events() -> List[Dict[str, Any]]:
    if not LOG_PATH.exists():
        return []

    with LOG_PATH.open(encoding="utf-8") as logfile:
        return [json.loads(line) for line in logfile if line.strip()]


def tune_after_rollback() -> Dict[str, Any]:
    events = _read_events()
    if not events:
        return {}

    last = events[-1]
    config = load_config()

    delta = last.get("delta", 0.0)
    psi_weight = float(config.get("psi_weight", 1.0))
    cvar_penalty = float(config.get("cvar_penalty", 0.4))

    if delta < -0.1:
        psi_weight *= 1.1
        cvar_penalty *= 1.05
        config["omega_threshold"] = min(0.99, float(config.get("omega_threshold", 0.85)) + 0.02)
    else:
        psi_weight *= 1.02

    config.update({"psi_weight": psi_weight, "cvar_penalty": cvar_penalty})
    save_config(config)

    return {"updated_config": config, "last_event": last}


if __name__ == "__main__":
    updated = tune_after_rollback()
    if updated:
        print("Config ajustada:", json.dumps(updated, indent=2, ensure_ascii=False))
    else:
        print("Nenhum rollback registrado ainda.")
