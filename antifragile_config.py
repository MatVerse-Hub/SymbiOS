from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path("antifragile_config.json")


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {
        "omega_threshold": 0.85,
        "psi_weight": 1.0,
        "cvar_penalty": 0.4,
        "cvar_alpha": 0.95,
        "window_size": 200,
    }


def save_config(data: Dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
