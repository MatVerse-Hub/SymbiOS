#!/usr/bin/env python3
"""
Kalman Policy Predictor - Autonomous Decision Making

Reutiliza o Filtro Kalman Adaptativo CFC como policy network para
prever ações ótimas de scaling, tuning e deployment.

State Vector: [Ω, Ψ, β, CPU, Latency]
Action Space: {scale_up, scale_down, retune, rollback, noop}

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum
import time


class Action(Enum):
    """Ações autônomas disponíveis"""
    SCALE_UP = "scale_up"           # Aumentar réplicas
    SCALE_DOWN = "scale_down"       # Reduzir réplicas
    RETUNE = "retune"               # Ajustar η, γ, τ
    ROLLBACK = "rollback"           # Reverter deployment
    NOOP = "noop"                   # Nenhuma ação necessária


@dataclass
class SystemState:
    """Estado completo do sistema MatVerse"""
    omega_score: float              # Ω(t) - Governança
    psi_index: float                # Ψ - Coerência Semântica
    beta_antifragile: float         # β - Coeficiente Antifrágil
    cpu_usage: float                # CPU % (0-1)
    latency_ms: float               # Latência em ms
    throughput: float               # Req/s
    timestamp: float = 0.0

    def to_vector(self) -> np.ndarray:
        """Converte estado para vetor numpy"""
        return np.array([
            self.omega_score,
            self.psi_index,
            self.beta_antifragile,
            self.cpu_usage,
            self.latency_ms / 1000.0,  # Normalizar para 0-1
        ])

    @classmethod
    def from_vector(cls, vec: np.ndarray, throughput: float = 0.0) -> 'SystemState':
        """Cria estado a partir de vetor"""
        return cls(
            omega_score=float(vec[0]),
            psi_index=float(vec[1]),
            beta_antifragile=float(vec[2]),
            cpu_usage=float(vec[3]),
            latency_ms=float(vec[4]) * 1000.0,
            throughput=throughput,
            timestamp=time.time()
        )


@dataclass
class PolicyPrediction:
    """Resultado da predição de policy"""
    action: Action
    confidence: float               # Confiança (0-1)
    predicted_state: SystemState
    reasoning: str
    processing_time_ms: float


class KalmanPolicyPredictor:
    """
    Policy Predictor baseado em Filtro Kalman Adaptativo

    Usa o framework CFC (Coerência-Fidelidade-Correlação) para
    prever estados futuros e selecionar ações ótimas.
    """

    def __init__(
        self,
        state_dim: int = 5,
        target_omega: float = 0.95,
        target_cpu: float = 0.70,
        target_latency: float = 100.0,  # ms
    ):
        self.state_dim = state_dim
        self.target_omega = target_omega
        self.target_cpu = target_cpu
        self.target_latency = target_latency

        # Matrizes do Filtro Kalman
        self.x = np.zeros(state_dim)           # Estado atual
        self.P = np.eye(state_dim) * 1.0       # Covariância do estado
        self.Q = np.eye(state_dim) * 0.01      # Ruído do processo (adaptativo)
        self.R = np.eye(state_dim) * 0.1       # Ruído da medição

        # Matriz de transição de estado (identidade inicialmente)
        self.F = np.eye(state_dim)

        # Histórico para aprendizado
        self.state_history: List[SystemState] = []
        self.max_history = 100

    def predict(
        self,
        current_state: SystemState,
        target: str = 'max_availability'
    ) -> Tuple[Action, PolicyPrediction]:
        """
        Prediz próxima ação ótima baseada no estado atual

        Args:
            current_state: Estado atual do sistema
            target: Objetivo ('max_availability', 'min_cost', 'balanced')

        Returns:
            (Action, PolicyPrediction) com ação e detalhes da predição
        """
        start_time = time.time()

        # Atualiza histórico
        self.state_history.append(current_state)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

        # Converte estado atual para vetor
        z = current_state.to_vector()

        # Passo 1: Predição Kalman
        x_pred = self.F @ self.x
        P_pred = self.F @ self.P @ self.F.T + self.Q

        # Passo 2: Atualização com medição
        y = z - x_pred  # Inovação
        S = P_pred + self.R  # Covariância da inovação
        K = P_pred @ np.linalg.inv(S)  # Ganho de Kalman

        self.x = x_pred + K @ y
        self.P = (np.eye(self.state_dim) - K) @ P_pred

        # Passo 3: Predição do próximo estado
        x_next = self.F @ self.x
        predicted_state = SystemState.from_vector(
            x_next,
            throughput=current_state.throughput
        )

        # Passo 4: Seleção de ação baseada em regras + predição
        action, confidence, reasoning = self._select_action(
            current_state,
            predicted_state,
            target
        )

        # Adapta ruído do processo baseado na qualidade da predição
        self._adapt_noise(y)

        processing_time = (time.time() - start_time) * 1000

        prediction = PolicyPrediction(
            action=action,
            confidence=confidence,
            predicted_state=predicted_state,
            reasoning=reasoning,
            processing_time_ms=processing_time
        )

        return action, prediction

    def _select_action(
        self,
        current: SystemState,
        predicted: SystemState,
        target: str
    ) -> Tuple[Action, float, str]:
        """
        Seleciona ação ótima baseada em estado atual e predito

        Lógica de decisão:
        1. CPU > 80% ou Latency > 200ms → SCALE_UP
        2. CPU < 30% e Latency < 50ms → SCALE_DOWN
        3. Ω < 0.7 → ROLLBACK
        4. β decrescente rápido → RETUNE
        5. Caso contrário → NOOP
        """
        confidence = 0.0
        reasoning = ""

        # Regra 1: Sobrecarga detectada ou prevista
        if current.cpu_usage > 0.80 or predicted.cpu_usage > 0.80:
            confidence = min(1.0, current.cpu_usage)
            reasoning = f"CPU alta: {current.cpu_usage:.1%} (pred: {predicted.cpu_usage:.1%})"
            return Action.SCALE_UP, confidence, reasoning

        if current.latency_ms > 200 or predicted.latency_ms > 200:
            confidence = min(1.0, current.latency_ms / 200)
            reasoning = f"Latência alta: {current.latency_ms:.0f}ms (pred: {predicted.latency_ms:.0f}ms)"
            return Action.SCALE_UP, confidence, reasoning

        # Regra 2: Subutilização (economizar recursos)
        if current.cpu_usage < 0.30 and current.latency_ms < 50:
            confidence = 1.0 - current.cpu_usage
            reasoning = f"Subutilização: CPU {current.cpu_usage:.1%}, Lat {current.latency_ms:.0f}ms"
            return Action.SCALE_DOWN, confidence, reasoning

        # Regra 3: Ω-Score crítico (qualidade baixa)
        if current.omega_score < 0.70:
            confidence = 1.0 - current.omega_score
            reasoning = f"Ω-Score crítico: {current.omega_score:.3f} < 0.70"
            return Action.ROLLBACK, confidence, reasoning

        # Regra 4: β decrescente rápido (perda de antifragilidade)
        if len(self.state_history) >= 3:
            beta_trend = self._calculate_trend('beta_antifragile')
            if beta_trend < -0.1:  # Queda de >10% recente
                confidence = abs(beta_trend)
                reasoning = f"β decrescente: tendência {beta_trend:.3f}"
                return Action.RETUNE, confidence, reasoning

        # Regra 5: Sistema estável
        confidence = current.omega_score
        reasoning = f"Sistema estável: Ω={current.omega_score:.3f}, CPU={current.cpu_usage:.1%}"
        return Action.NOOP, confidence, reasoning

    def _calculate_trend(self, metric: str) -> float:
        """Calcula tendência de uma métrica no histórico recente"""
        if len(self.state_history) < 3:
            return 0.0

        recent = self.state_history[-5:]
        values = [getattr(s, metric) for s in recent]

        # Regressão linear simples
        n = len(values)
        x = np.arange(n)
        y = np.array(values)

        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / \
                (n * np.sum(x**2) - np.sum(x)**2)

        return slope

    def _adapt_noise(self, innovation: np.ndarray):
        """
        Adapta matrizes de ruído baseado na qualidade da predição

        Se inovação é grande → aumenta Q (processo mais ruidoso)
        Se inovação é pequena → reduz Q (processo mais determinístico)
        """
        innovation_norm = np.linalg.norm(innovation)

        # Escala adaptativa: [0.001, 0.1]
        scale = np.clip(innovation_norm, 0.001, 0.1)
        self.Q = np.eye(self.state_dim) * scale

    def reset(self):
        """Reseta estado do filtro"""
        self.x = np.zeros(self.state_dim)
        self.P = np.eye(self.state_dim) * 1.0
        self.state_history.clear()


# === FUNÇÕES DE TESTE E DEMO ===

def demo_policy_predictor():
    """Demonstração do KalmanPolicyPredictor"""
    print("=" * 80)
    print("🧠 KALMAN POLICY PREDICTOR - DEMONSTRAÇÃO")
    print("=" * 80)

    predictor = KalmanPolicyPredictor()

    # Simula sequência de estados
    scenarios = [
        SystemState(0.95, 0.98, 1.2, 0.45, 50, 1500),  # Normal
        SystemState(0.94, 0.97, 1.18, 0.65, 85, 2200),  # Carga aumentando
        SystemState(0.92, 0.95, 1.15, 0.82, 150, 2800),  # Alta carga
        SystemState(0.88, 0.91, 1.10, 0.25, 30, 800),  # Baixa carga
        SystemState(0.65, 0.70, 0.95, 0.55, 120, 1200),  # Ω crítico
    ]

    scenario_names = [
        "Normal Operation",
        "Increasing Load",
        "High Load",
        "Low Load",
        "Critical Ω-Score"
    ]

    for i, (state, name) in enumerate(zip(scenarios, scenario_names)):
        print(f"\n📊 Cenário {i+1}: {name}")
        print(f"   Estado: Ω={state.omega_score:.3f}, CPU={state.cpu_usage:.1%}, "
              f"Lat={state.latency_ms:.0f}ms, β={state.beta_antifragile:.3f}")

        action, prediction = predictor.predict(state)

        print(f"   ✅ Ação: {action.value}")
        print(f"   📈 Confiança: {prediction.confidence:.3f}")
        print(f"   💭 Reasoning: {prediction.reasoning}")
        print(f"   ⏱️  Tempo: {prediction.processing_time_ms:.2f}ms")
        print(f"   🔮 Estado predito: Ω={prediction.predicted_state.omega_score:.3f}, "
              f"CPU={prediction.predicted_state.cpu_usage:.1%}")

    print("\n" + "=" * 80)
    print("✅ Demonstração concluída com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    demo_policy_predictor()
