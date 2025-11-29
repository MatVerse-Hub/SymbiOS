from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean
from threading import Thread
from typing import Dict, Iterable, List, Tuple

if importlib.util.find_spec("prometheus_client"):
    from prometheus_client import Gauge, start_http_server
else:
    _fallback_gauges = []

    class Gauge:  # type: ignore[misc]
        def __init__(self, name: str, description: str) -> None:
            self.name = name
            self.description = description
            self.value: float = 0.0
            _fallback_gauges.append(self)

        def set(self, value: float) -> None:
            try:
                self.value = float(value)
            except (TypeError, ValueError):
                self.value = 0.0

    def start_http_server(port: int) -> None:  # type: ignore[misc]
        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - inherited API
                if self.path not in {"/metrics", "/"}:
                    self.send_response(404)
                    self.end_headers()
                    return

                lines = []
                for gauge in _fallback_gauges:
                    lines.append(f"# HELP {gauge.name} {gauge.description}")
                    lines.append(f"# TYPE {gauge.name} gauge")
                    lines.append(f"{gauge.name} {gauge.value}")
                body = "\n".join(lines) + "\n"

                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4")
                self.send_header("Content-Length", str(len(body.encode("utf-8"))))
                self.end_headers()
                self.wfile.write(body.encode("utf-8"))

            def log_message(self, format: str, *args: object) -> None:  # noqa: A003
                return

        logging.getLogger(__name__).warning(
            "prometheus_client indisponível; usando servidor de métricas embutido."
        )
        server = ThreadingHTTPServer(("0.0.0.0", port), MetricsHandler)
        Thread(target=server.serve_forever, daemon=True).start()

from antifragile_config import load_config

OMEGA = Gauge("symbios_omega_score", "Ω-Score atual")
PSI = Gauge("symbios_psi_score", "Ψ-Score atual")
CVAR = Gauge("symbios_cvar_score", "CVaR atual")

EVIDENCE_PATH = Path("symbios/evidence.json")


def _tail_mean(values: Iterable[float], alpha: float) -> float:
    ordered = sorted(values, reverse=True)
    if not ordered:
        return 0.0

    cutoff = max(1, int(len(ordered) * (1 - alpha)))
    tail = ordered[:cutoff]
    return mean(tail)


def _load_recent_events(limit: int) -> List[Dict]:
    if not EVIDENCE_PATH.exists():
        return []

    try:
        data = EVIDENCE_PATH.read_text(encoding="utf-8")
        events = json.loads(data)
        if not isinstance(events, list):
            return []
        return events[-limit:]
    except json.JSONDecodeError:
        return []


def get_omega_psi_cvar(window: int | None = None, alpha: float | None = None) -> Tuple[float, float, float]:
    config = load_config()
    window_size = window or int(config.get("window_size", 200))
    alpha_value = alpha or float(config.get("cvar_alpha", 0.95))
    events = _load_recent_events(window_size)

    if not events:
        fallback = float(config.get("omega_threshold", 0.85))
        return fallback, fallback, 0.0

    psi_scores: List[float] = []
    for event in events:
        gate = event.get("omega_gate", {}) if isinstance(event, dict) else {}
        psi_value = gate.get("psi") if isinstance(gate, dict) else None
        if psi_value is None:
            continue
        try:
            psi_scores.append(float(psi_value))
        except (TypeError, ValueError):
            continue

    if not psi_scores:
        fallback = float(config.get("omega_threshold", 0.85))
        return fallback, fallback, 0.0

    psi_score = mean(psi_scores)
    losses = [max(0.0, 1.0 - psi) for psi in psi_scores]
    cvar_score = _tail_mean(losses, alpha_value)

    psi_weight = float(config.get("psi_weight", 1.0))
    cvar_penalty = float(config.get("cvar_penalty", 0.0))
    omega_score = max(0.0, min(1.0, psi_weight * psi_score - cvar_penalty * cvar_score))

    return omega_score, psi_score, cvar_score


def _update_metrics(window: int, alpha: float) -> Tuple[float, float, float]:
    omega, psi, cvar = get_omega_psi_cvar(window=window, alpha=alpha)
    OMEGA.set(omega)
    PSI.set(psi)
    CVAR.set(cvar)
    return omega, psi, cvar


def main() -> None:
    parser = argparse.ArgumentParser(description="Expose Ω/Ψ/CVaR metrics for SymbiOS")
    parser.add_argument("--port", type=int, default=8000, help="Porta para expor métricas Prometheus")
    parser.add_argument("--interval", type=int, default=10, help="Intervalo de coleta em segundos")
    parser.add_argument("--window", type=int, default=None, help="Quantidade de eventos recentes para cálculo")
    parser.add_argument("--alpha", type=float, default=None, help="Nível de confiança para CVaR (0-1)")
    parser.add_argument("--once", action="store_true", help="Executa uma coleta única e imprime valores")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")

    if args.once:
        omega, psi, cvar = _update_metrics(window=args.window or 200, alpha=args.alpha or 0.95)
        print(f"omega={omega:.4f} psi={psi:.4f} cvar={cvar:.4f}")
        return

    start_http_server(args.port)
    logging.info("Ω exporter rodando na porta %s", args.port)
    while True:
        omega, psi, cvar = _update_metrics(window=args.window or 200, alpha=args.alpha or 0.95)
        logging.info("Ω=%s Ψ=%s CVaR=%s", round(omega, 4), round(psi, 4), round(cvar, 4))
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
