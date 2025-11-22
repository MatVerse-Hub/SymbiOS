#!/usr/bin/env python3
"""
Decision Engine - Loop OODA Autônomo

Implementa o loop Observe-Orient-Decide-Act em <200ms total:
- Observe: 10ms (coleta métricas)
- Orient: 50ms (predição Kalman)
- Decide: 50ms (seleção de ação)
- Act: 90ms (execução via actuator)

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import time
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field
import threading
from enum import Enum

from .kalman_policy import (
    KalmanPolicyPredictor,
    SystemState,
    Action,
    PolicyPrediction
)
from .metrics_collector import MatVerseMetricsCollector


class DecisionMode(Enum):
    """Modo de operação do Decision Engine"""
    CONSERVATIVE = "conservative"       # Só age em situações críticas
    BALANCED = "balanced"              # Balanceia estabilidade e eficiência
    AGGRESSIVE = "aggressive"          # Otimiza performance ativamente


@dataclass
class Decision:
    """Decisão autônoma tomada pelo engine"""
    action: Action
    confidence: float
    reasoning: str
    system_state: SystemState
    predicted_state: SystemState
    metrics_snapshot: Dict[str, float]
    mode: DecisionMode
    timestamp: float = field(default_factory=time.time)
    processing_time_ms: float = 0.0

    # Performance breakdown
    observe_time_ms: float = 0.0
    orient_time_ms: float = 0.0
    decide_time_ms: float = 0.0


class DecisionEngine:
    """
    Motor de decisão autônomo do MatVerse

    Implementa loop OODA fechado para autonomia completa:
    zero-touch, zero-downtime, zero-human-intervention.
    """

    def __init__(
        self,
        metrics_collector: MatVerseMetricsCollector,
        mode: DecisionMode = DecisionMode.BALANCED,
        decision_interval: float = 5.0,  # Decisões a cada 5s
        min_confidence: float = 0.70,    # Confiança mínima para agir
    ):
        self.metrics_collector = metrics_collector
        self.mode = mode
        self.decision_interval = decision_interval
        self.min_confidence = min_confidence

        # Policy predictor
        self.policy_predictor = KalmanPolicyPredictor(
            target_omega=0.95,
            target_cpu=0.70,
            target_latency=100.0
        )

        # Histórico de decisões
        self.decision_history: List[Decision] = []
        self.max_history = 1000

        # Thread de decisão autônoma
        self._decision_thread: Optional[threading.Thread] = None
        self._stop_decisions = threading.Event()
        self._last_decision: Optional[Decision] = None

        # Callbacks para ações
        self._action_callbacks: Dict[Action, callable] = {}

    def register_action_callback(self, action: Action, callback: callable):
        """
        Registra callback para ser executado quando uma ação é decidida

        Args:
            action: Tipo de ação
            callback: Função callback(decision: Decision) -> bool
        """
        self._action_callbacks[action] = callback

    def start_autonomous_loop(self):
        """Inicia loop de decisão autônomo"""
        if self._decision_thread and self._decision_thread.is_alive():
            return

        self._stop_decisions.clear()
        self._decision_thread = threading.Thread(
            target=self._autonomous_decision_loop,
            daemon=True
        )
        self._decision_thread.start()

    def stop_autonomous_loop(self):
        """Para loop de decisão autônomo"""
        self._stop_decisions.set()
        if self._decision_thread:
            self._decision_thread.join(timeout=2.0)

    def _autonomous_decision_loop(self):
        """Loop principal de decisão autônoma"""
        while not self._stop_decisions.is_set():
            try:
                decision = self.make_decision()
                self._last_decision = decision

                # Executa callback se ação não for NOOP
                if decision.action != Action.NOOP:
                    callback = self._action_callbacks.get(decision.action)
                    if callback:
                        try:
                            callback(decision)
                        except Exception as e:
                            print(f"❌ Erro executando callback {decision.action}: {e}")

            except Exception as e:
                print(f"❌ Erro no loop de decisão: {e}")

            time.sleep(self.decision_interval)

    def make_decision(self) -> Decision:
        """
        Toma uma decisão autônoma baseada no estado atual

        Loop OODA completo:
        1. Observe (10ms): Coleta métricas
        2. Orient (50ms): Predição Kalman
        3. Decide (50ms): Seleção de ação
        4. Act (delegado ao actuator)

        Returns:
            Decision com ação, confiança e reasoning
        """
        start_time = time.time()

        # === OBSERVE (10ms) ===
        observe_start = time.time()

        metrics = self.metrics_collector.get_snapshot()

        # Extrai métricas principais
        omega_score = self.metrics_collector.get_current_value("omega_score_current", default=0.9)
        psi_index = self.metrics_collector.get_current_value("psi_index_current", default=0.95)
        beta_antifragile = self.metrics_collector.get_current_value("beta_antifragile_current", default=1.0)
        cpu_usage = self.metrics_collector.get_current_value("system_cpu_usage", default=0.5)
        latency_ms = self.metrics_collector.get_current_value("latency_ms", default=50.0)
        throughput = self.metrics_collector.get_current_value("throughput_rps", default=1000.0)

        system_state = SystemState(
            omega_score=omega_score,
            psi_index=psi_index,
            beta_antifragile=beta_antifragile,
            cpu_usage=cpu_usage,
            latency_ms=latency_ms,
            throughput=throughput,
            timestamp=time.time()
        )

        observe_time = (time.time() - observe_start) * 1000

        # === ORIENT (50ms) ===
        orient_start = time.time()

        # Target baseado no modo
        target = self._get_target_from_mode()

        action, policy_prediction = self.policy_predictor.predict(
            system_state,
            target=target
        )

        orient_time = (time.time() - orient_start) * 1000

        # === DECIDE (50ms) ===
        decide_start = time.time()

        # Aplica filtros baseados no modo e confiança mínima
        final_action, confidence, reasoning = self._apply_decision_filters(
            action,
            policy_prediction.confidence,
            policy_prediction.reasoning,
            system_state
        )

        decide_time = (time.time() - decide_start) * 1000

        # Cria decisão
        decision = Decision(
            action=final_action,
            confidence=confidence,
            reasoning=reasoning,
            system_state=system_state,
            predicted_state=policy_prediction.predicted_state,
            metrics_snapshot=metrics,
            mode=self.mode,
            processing_time_ms=(time.time() - start_time) * 1000,
            observe_time_ms=observe_time,
            orient_time_ms=orient_time,
            decide_time_ms=decide_time
        )

        # Adiciona ao histórico
        self.decision_history.append(decision)
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)

        return decision

    def _get_target_from_mode(self) -> str:
        """Retorna target baseado no modo de operação"""
        if self.mode == DecisionMode.CONSERVATIVE:
            return 'max_availability'
        elif self.mode == DecisionMode.AGGRESSIVE:
            return 'min_cost'
        else:  # BALANCED
            return 'balanced'

    def _apply_decision_filters(
        self,
        action: Action,
        confidence: float,
        reasoning: str,
        state: SystemState
    ) -> Tuple[Action, float, str]:
        """
        Aplica filtros de decisão baseados no modo

        CONSERVATIVE: Só age se confiança > 0.85
        BALANCED: Só age se confiança > 0.70
        AGGRESSIVE: Age mesmo com confiança > 0.50
        """
        # Threshold de confiança por modo
        thresholds = {
            DecisionMode.CONSERVATIVE: 0.85,
            DecisionMode.BALANCED: 0.70,
            DecisionMode.AGGRESSIVE: 0.50,
        }

        threshold = thresholds.get(self.mode, 0.70)

        # Se confiança insuficiente → NOOP
        if confidence < threshold and action != Action.NOOP:
            return (
                Action.NOOP,
                confidence,
                f"Confiança {confidence:.2f} < threshold {threshold:.2f} ({self.mode.value}). Original: {reasoning}"
            )

        # Conservative: evita SCALE_DOWN agressivo
        if self.mode == DecisionMode.CONSERVATIVE and action == Action.SCALE_DOWN:
            if state.omega_score > 0.90:  # Sistema estável
                return action, confidence, reasoning
            else:
                return (
                    Action.NOOP,
                    confidence,
                    f"Conservative mode: evitando scale_down com Ω={state.omega_score:.3f}"
                )

        # Aggressive: favorece SCALE_UP preventivo
        if self.mode == DecisionMode.AGGRESSIVE and action == Action.NOOP:
            if state.cpu_usage > 0.60 or state.latency_ms > 80:
                return (
                    Action.SCALE_UP,
                    0.75,
                    f"Aggressive mode: scale_up preventivo (CPU={state.cpu_usage:.1%}, Lat={state.latency_ms:.0f}ms)"
                )

        return action, confidence, reasoning

    def get_last_decision(self) -> Optional[Decision]:
        """Retorna última decisão tomada"""
        return self._last_decision

    def get_decision_history(self, limit: int = 100) -> List[Decision]:
        """Retorna histórico de decisões"""
        return self.decision_history[-limit:]

    def get_statistics(self) -> Dict:
        """Retorna estatísticas do Decision Engine"""
        if not self.decision_history:
            return {}

        recent = self.decision_history[-100:]

        action_counts = {}
        for d in recent:
            action_counts[d.action.value] = action_counts.get(d.action.value, 0) + 1

        avg_processing_time = sum(d.processing_time_ms for d in recent) / len(recent)
        avg_observe_time = sum(d.observe_time_ms for d in recent) / len(recent)
        avg_orient_time = sum(d.orient_time_ms for d in recent) / len(recent)
        avg_decide_time = sum(d.decide_time_ms for d in recent) / len(recent)

        return {
            'total_decisions': len(self.decision_history),
            'recent_decisions': len(recent),
            'action_distribution': action_counts,
            'avg_processing_time_ms': avg_processing_time,
            'avg_observe_time_ms': avg_observe_time,
            'avg_orient_time_ms': avg_orient_time,
            'avg_decide_time_ms': avg_decide_time,
            'mode': self.mode.value,
        }


# === FUNÇÕES DE TESTE E DEMO ===

def demo_decision_engine():
    """Demonstração do DecisionEngine"""
    print("=" * 80)
    print("🧠 DECISION ENGINE - DEMONSTRAÇÃO LOOP OODA")
    print("=" * 80)

    # Setup
    collector = MatVerseMetricsCollector(collection_interval=0.5)
    collector.start_auto_collection()

    engine = DecisionEngine(
        metrics_collector=collector,
        mode=DecisionMode.BALANCED,
        decision_interval=1.0
    )

    # Callbacks de exemplo
    def on_scale_up(decision: Decision):
        print(f"   🚀 EXECUTANDO SCALE_UP: {decision.reasoning}")

    def on_scale_down(decision: Decision):
        print(f"   📉 EXECUTANDO SCALE_DOWN: {decision.reasoning}")

    engine.register_action_callback(Action.SCALE_UP, on_scale_up)
    engine.register_action_callback(Action.SCALE_DOWN, on_scale_down)

    # Simula cenários
    import random

    scenarios = [
        ("Normal", 0.95, 0.97, 1.2, 0.45, 50, 1500),
        ("Carga Alta", 0.92, 0.94, 1.15, 0.85, 180, 2500),
        ("Carga Baixa", 0.93, 0.96, 1.18, 0.20, 30, 800),
        ("Crítico", 0.65, 0.72, 0.95, 0.75, 250, 1800),
    ]

    print("\n🔄 Executando 4 decisões autônomas...")

    for i, (name, omega, psi, beta, cpu, lat, thr) in enumerate(scenarios):
        # Atualiza métricas
        collector.update_matverse_metrics(omega, psi, beta, lat, thr)

        # Faz decisão
        decision = engine.make_decision()

        print(f"\n📊 Decisão {i+1}: {name}")
        print(f"   Estado: Ω={omega:.3f}, CPU={cpu:.1%}, Lat={lat:.0f}ms")
        print(f"   ✅ Ação: {decision.action.value} (confiança: {decision.confidence:.3f})")
        print(f"   💭 Reasoning: {decision.reasoning}")
        print(f"   ⏱️  OODA Loop: {decision.processing_time_ms:.2f}ms total")
        print(f"      Observe: {decision.observe_time_ms:.2f}ms")
        print(f"      Orient: {decision.orient_time_ms:.2f}ms")
        print(f"      Decide: {decision.decide_time_ms:.2f}ms")

        time.sleep(0.3)

    # Estatísticas
    print("\n📈 Estatísticas:")
    stats = engine.get_statistics()
    print(f"   Total de decisões: {stats['total_decisions']}")
    print(f"   Distribuição de ações: {stats['action_distribution']}")
    print(f"   Tempo médio OODA: {stats['avg_processing_time_ms']:.2f}ms")

    collector.stop_auto_collection()

    print("\n" + "=" * 80)
    print("✅ Demonstração concluída!")
    print("=" * 80)


if __name__ == "__main__":
    demo_decision_engine()
