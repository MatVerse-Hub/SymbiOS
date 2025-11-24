from __future__ import annotations

import json
from typing import Any, Dict, Mapping, MutableMapping

TAU = 0.85


def compute_subscores(s: Mapping[str, Any]) -> Dict[str, float]:
    # Preserve separation between input/output/context even if malformed payloads arrive
    output_payload = s.get("output") if isinstance(s, Mapping) else {}
    input_payload: MutableMapping[str, Any] = s.get("input") if isinstance(s, Mapping) else {}
    context_payload = s.get("context") if isinstance(s, Mapping) else {}

    output_text = ""
    if isinstance(output_payload, Mapping):
        output_text = str(output_payload.get("text", ""))

    if not isinstance(input_payload, Mapping):
        input_payload = {}

    if not isinstance(context_payload, Mapping):
        context_payload = {}

    return {
        "format": 1.0 if _is_json(output_text) else 0.0,
        "policy": 1.0 if not _violates_policy(output_text) else 0.0,
        "consistency": _heuristic_consistency(output_text),
        "coverage": _heuristic_coverage(input_payload, output_text, context_payload),
    }


def compute_psi(subscores: Dict[str, float]) -> float:
    weights = {"format": 0.25, "policy": 0.25, "consistency": 0.25, "coverage": 0.25}
    return sum(weights.get(k, 0.0) * v for k, v in subscores.items())


def omega_gate(s: Dict[str, Any]) -> Dict[str, Any]:
    subscores = compute_subscores(s)
    psi = compute_psi(subscores)
    return {
        "approved": psi >= TAU,
        "psi": psi,
        "threshold": TAU,
        "subscores": subscores,
    }


def _is_json(text: str) -> bool:
    text = text.strip()
    if not text:
        return False

    if text.startswith("{") or text.startswith("["):
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False
    return False


def _violates_policy(text: str) -> bool:
    banned_terms = ["violation", "malware", "exploit"]
    lowered = text.lower()
    return any(term in lowered for term in banned_terms)


def _heuristic_consistency(text: str) -> float:
    if not text:
        return 0.0

    balanced_braces = text.count("{") == text.count("}")
    balanced_brackets = text.count("[") == text.count("]")
    punctuation_balance = 1.0 if balanced_braces and balanced_brackets else 0.6

    line_breaks = text.count("\n")
    formatting_penalty = 0.05 * min(line_breaks, 4)

    return max(0.0, 1.0 - formatting_penalty) * punctuation_balance


def _heuristic_coverage(inp: Dict[str, Any], out: str, ctx: Dict[str, Any]) -> float:
    expected_format = ctx.get("expected_format")
    mentioned_keys = sum(1 for key in inp.keys() if str(key) in out)
    key_coverage = mentioned_keys / max(len(inp), 1)

    if expected_format:
        format_hint = expected_format.lower()
        format_present = format_hint in out.lower()
    else:
        format_present = True

    return min(1.0, 0.7 * key_coverage + (0.3 if format_present else 0.0))
