from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict

from antifragile_config import load_config, save_config

LOG_PATH = Path("antifragile_log.jsonl")


def log_rollback(omega_old: float, omega_new: float) -> Dict[str, Any]:
    timestamp = datetime.datetime.utcnow().isoformat()
    event = {
        "timestamp": timestamp,
        "omega_old": omega_old,
        "omega_new": omega_new,
        "delta": omega_new - omega_old,
        "antifragile_gain": max(0.0, omega_new - omega_old),
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.touch()

    with LOG_PATH.open("a", encoding="utf-8") as logfile:
        logfile.write(json.dumps(event) + "\n")

    return event


def record_failure_threshold_breach(current_omega: float) -> None:
    config = load_config()
    tuned = dict(config)
    tuned["omega_threshold"] = min(0.99, max(config.get("omega_threshold", 0.85), current_omega + 0.02))
    save_config(tuned)


def log_and_tune(omega_old: float, omega_new: float) -> Dict[str, Any]:
    event = log_rollback(omega_old, omega_new)
    record_failure_threshold_breach(omega_new)
    return event
