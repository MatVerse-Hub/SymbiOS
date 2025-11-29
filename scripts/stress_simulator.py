from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

import requests

from symbios.backend.omega_gate import omega_gate
from symbios.backend.pose_lite import register_evidence


def _build_payload(intensity: float) -> Dict[str, Any]:
    noisy_text = "{}" if intensity < 0.5 else "[[malformed-output"  # prejudica formato/consistência
    banned = " malware" if intensity > 0.75 else ""

    input_body = {"query": "status", "user": "tester", "intensity": intensity}
    output_body = {"text": f"{noisy_text}{banned}"}
    context_body = {"expected_format": "json"}

    return {"model": "stress-simulator", "input": input_body, "output": output_body, "context": context_body}


def _send_online(server: str, payload: Dict[str, Any]) -> None:
    url = f"{server.rstrip('/')}/symbios/ia/invoke"
    response = requests.post(url, json=payload, timeout=5)
    response.raise_for_status()


def _register_offline(payload: Dict[str, Any]) -> None:
    gate_result = omega_gate(payload)
    register_evidence(payload, gate_result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador de estresse para antifragilidade Ω/Ψ/CVaR")
    parser.add_argument("--server", default="", help="Endpoint FastAPI do SymbiOS (se vazio usa modo offline)")
    parser.add_argument("--intensity", type=float, default=0.9, help="De 0 a 1: severidade do estresse")
    parser.add_argument("--events", type=int, default=10, help="Número de eventos sintetizados")
    args = parser.parse_args()

    failures = 0
    for _ in range(args.events):
        payload = _build_payload(args.intensity)
        if args.server:
            try:
                _send_online(args.server, payload)
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"Falha ao enviar para {args.server}: {exc}")
                _register_offline(payload)
        else:
            _register_offline(payload)

    mode = "online" if args.server else "offline"
    summary = {"mode": mode, "events": args.events, "failures": failures, "intensity": args.intensity}
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
