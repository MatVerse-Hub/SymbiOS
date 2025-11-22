#!/usr/bin/env python3
"""
Filtro Kalman Adaptativo CFC (Coerência-Fidelidade-Correlação)
MatVerse Unified Ecosystem - Quantum State Enhancement

Implementa filtro Kalman adaptativo para otimização de estados quânticos
com foco em correlação Ψ-Γ e maximização de fidelidade quântica.

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
import time


@dataclass
class KalmanState:
    """Estado do filtro Kalman adaptativo"""
    x: np.ndarray  # Vetor de estado [Ψ, Γ]
    P: np.ndarray  # Matriz de covariância
    Q: np.ndarray  # Ruído do processo
    R: np.ndarray  # Ruído da medição
    K: np.ndarray  # Ganho de Kalman
    iteration: int = 0


class AdaptiveKalmanCFC:
    """
    Filtro Kalman Adaptativo para otimização CFC

    CFC = Coerência-Fidelidade-Correlação
    - Coerência: Manutenção de fase quântica
    - Fidelidade: F = |⟨Ψ|Φ⟩|² (fidelidade de estado)
    - Correlação: corr(Ψ, Γ) (correlação entre estados)
    """

    def __init__(self,
                 initial_psi: float = 0.0,
                 initial_gamma: float = 0.0,
                 process_noise: float = 0.01,
                 measurement_noise: float = 0.05):
        """
        Inicializa o filtro Kalman adaptativo

        Args:
            initial_psi: Valor inicial de Ψ
            initial_gamma: Valor inicial de Γ
            process_noise: Variância do ruído do processo
            measurement_noise: Variância do ruído de medição
        """
        # Estado inicial [Ψ, Γ]
        self.x = np.array([initial_psi, initial_gamma])

        # Matriz de covariância inicial
        self.P = np.eye(2) * 1.0

        # Ruído do processo (Q) e medição (R)
        self.Q = np.eye(2) * process_noise
        self.R = np.eye(2) * measurement_noise

        # Matriz de transição de estado (identidade para sistema estacionário)
        self.F = np.eye(2)

        # Matriz de observação (medimos diretamente Ψ e Γ)
        self.H = np.eye(2)

        # Histórico
        self.history: List[KalmanState] = []
        self.iteration = 0

    def predict(self) -> np.ndarray:
        """
        Fase de predição do filtro Kalman

        Returns:
            Estado predito [Ψ, Γ]
        """
        # Predição do estado: x̂⁻ = F·x̂
        self.x = self.F @ self.x

        # Predição da covariância: P⁻ = F·P·Fᵀ + Q
        self.P = self.F @ self.P @ self.F.T + self.Q

        return self.x

    def update(self, measurement: np.ndarray) -> np.ndarray:
        """
        Fase de atualização do filtro Kalman

        Args:
            measurement: Medição [Ψ_measured, Γ_measured]

        Returns:
            Estado atualizado [Ψ, Γ]
        """
        # Inovação: y = z - H·x̂⁻
        y = measurement - self.H @ self.x

        # Covariância da inovação: S = H·P⁻·Hᵀ + R
        S = self.H @ self.P @ self.H.T + self.R

        # Ganho de Kalman: K = P⁻·Hᵀ·S⁻¹
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Atualização do estado: x̂ = x̂⁻ + K·y
        self.x = self.x + K @ y

        # Atualização da covariância: P = (I - K·H)·P⁻
        I = np.eye(2)
        self.P = (I - K @ self.H) @ self.P

        # Salva ganho para análise
        self.K_last = K

        return self.x

    def adapt_noise(self, innovation: np.ndarray):
        """
        Adaptação automática das matrizes de ruído Q e R
        baseada na inovação observada

        Args:
            innovation: Vetor de inovação
        """
        # Calcula magnitude da inovação
        inn_norm = np.linalg.norm(innovation)

        # Adapta Q (ruído do processo)
        if inn_norm > 0.5:
            # Alta inovação → aumenta Q (mais incerteza no modelo)
            self.Q *= 1.1
        elif inn_norm < 0.1:
            # Baixa inovação → reduz Q (modelo mais confiável)
            self.Q *= 0.9

        # Limita Q para evitar instabilidade
        self.Q = np.clip(self.Q, 1e-6, 1.0)

    def process_measurement(self,
                          psi_measured: float,
                          gamma_measured: float) -> Tuple[np.ndarray, Dict]:
        """
        Processa uma medição completa (predição + atualização + adaptação)

        Args:
            psi_measured: Valor medido de Ψ
            gamma_measured: Valor medido de Γ

        Returns:
            Tupla (estado_estimado, métricas)
        """
        self.iteration += 1

        # Fase de predição
        x_pred = self.predict()

        # Medição
        z = np.array([psi_measured, gamma_measured])

        # Inovação antes da atualização
        innovation = z - self.H @ x_pred

        # Fase de atualização
        x_updated = self.update(z)

        # Adaptação automática
        self.adapt_noise(innovation)

        # Salva estado no histórico
        state = KalmanState(
            x=x_updated.copy(),
            P=self.P.copy(),
            Q=self.Q.copy(),
            R=self.R.copy(),
            K=self.K_last.copy(),
            iteration=self.iteration
        )
        self.history.append(state)

        # Métricas
        metrics = {
            'iteration': self.iteration,
            'psi_estimated': float(x_updated[0]),
            'gamma_estimated': float(x_updated[1]),
            'innovation_norm': float(np.linalg.norm(innovation)),
            'kalman_gain': float(np.mean(np.abs(self.K_last))),
            'covariance_trace': float(np.trace(self.P)),
            'process_noise': float(np.mean(np.diag(self.Q))),
            'measurement_noise': float(np.mean(np.diag(self.R)))
        }

        return x_updated, metrics

    def calculate_correlation(self, psi_series: List[float],
                            gamma_series: List[float]) -> float:
        """
        Calcula correlação entre séries Ψ e Γ

        Args:
            psi_series: Série temporal de Ψ
            gamma_series: Série temporal de Γ

        Returns:
            Coeficiente de correlação de Pearson
        """
        psi_arr = np.array(psi_series)
        gamma_arr = np.array(gamma_series)

        # Correlação de Pearson
        corr_matrix = np.corrcoef(psi_arr, gamma_arr)
        correlation = corr_matrix[0, 1]

        return float(correlation)

    def calculate_fidelity(self, target_psi: float = 1.0,
                          target_gamma: float = -1.0) -> float:
        """
        Calcula fidelidade quântica F = |⟨Ψ|Φ⟩|²

        Aproximação: F ≈ exp(-d²/2σ²)
        onde d = distância euclidiana ao estado alvo

        Args:
            target_psi: Valor alvo de Ψ
            target_gamma: Valor alvo de Γ

        Returns:
            Fidelidade (0 a 1)
        """
        target = np.array([target_psi, target_gamma])
        distance = np.linalg.norm(self.x - target)

        # Fidelidade gaussiana
        sigma = 1.0
        fidelity = np.exp(-distance**2 / (2 * sigma**2))

        return float(fidelity)

    def optimize_cfc(self,
                     psi_series: List[float],
                     gamma_series: List[float],
                     max_iterations: int = 50,
                     correlation_threshold: float = -0.95) -> Dict:
        """
        Otimização completa CFC (Coerência-Fidelidade-Correlação)

        Args:
            psi_series: Série temporal de medições Ψ
            gamma_series: Série temporal de medições Γ
            max_iterations: Número máximo de iterações
            correlation_threshold: Limiar de correlação desejado

        Returns:
            Dicionário com resultados da otimização
        """
        if len(psi_series) != len(gamma_series):
            raise ValueError("psi_series e gamma_series devem ter o mesmo tamanho")

        start_time = time.time()

        # Calcula correlação inicial
        corr_initial = self.calculate_correlation(psi_series, gamma_series)

        # Processa todas as medições
        psi_filtered = []
        gamma_filtered = []

        for psi_m, gamma_m in zip(psi_series, gamma_series):
            x_est, metrics = self.process_measurement(psi_m, gamma_m)
            psi_filtered.append(x_est[0])
            gamma_filtered.append(x_est[1])

        # Iterações adicionais para convergência
        iterations = len(psi_series)
        for _ in range(max_iterations - len(psi_series)):
            # Usa últimas medições para continuar filtragem
            x_est, _ = self.process_measurement(psi_series[-1], gamma_series[-1])
            psi_filtered.append(x_est[0])
            gamma_filtered.append(x_est[1])
            iterations += 1

            # Verifica convergência
            if len(psi_filtered) >= 5:
                recent_corr = self.calculate_correlation(
                    psi_filtered[-5:],
                    gamma_filtered[-5:]
                )
                if recent_corr <= correlation_threshold:
                    break

        # Calcula correlação final
        corr_final = self.calculate_correlation(psi_filtered, gamma_filtered)

        # Calcula fidelidade
        fidelity = self.calculate_fidelity()

        # Calcula métricas CFC
        coerência = 1.0 - np.mean(np.diag(self.P))  # Baixa covariância = alta coerência

        processing_time = (time.time() - start_time) * 1000  # ms

        results = {
            'success': True,
            'iterations': iterations,
            'correlation_initial': corr_initial,
            'correlation_final': corr_final,
            'correlation_gain': corr_final - corr_initial,
            'fidelity': fidelity,
            'coherence': coerência,
            'cfc_score': (abs(corr_final) + fidelity + coerência) / 3,
            'psi_final': float(self.x[0]),
            'gamma_final': float(self.x[1]),
            'processing_time_ms': processing_time,
            'converged': corr_final <= correlation_threshold
        }

        return results


def demo_kalman_adaptive():
    """Demonstração do Filtro Kalman Adaptativo CFC"""
    print("🧮 FILTRO KALMAN ADAPTATIVO CFC - DEMONSTRAÇÃO")
    print("=" * 60)

    # Cria séries de medições sintéticas
    # Ψ e Γ idealmente anticorrelacionados (Ψ↑ → Γ↓)
    np.random.seed(42)
    n_samples = 20

    psi_true = np.linspace(-1, 1, n_samples)
    gamma_true = -psi_true + np.random.normal(0, 0.1, n_samples)

    # Adiciona ruído de medição
    psi_measured = psi_true + np.random.normal(0, 0.2, n_samples)
    gamma_measured = gamma_true + np.random.normal(0, 0.2, n_samples)

    # Cria filtro
    kalman = AdaptiveKalmanCFC()

    # Executa otimização CFC
    results = kalman.optimize_cfc(
        psi_measured.tolist(),
        gamma_measured.tolist(),
        max_iterations=50,
        correlation_threshold=-0.95
    )

    # Exibe resultados
    print(f"✅ Otimização concluída!")
    print(f"📊 Iterações: {results['iterations']}")
    print(f"📈 Correlação inicial: {results['correlation_initial']:.3f}")
    print(f"🎯 Correlação final: {results['correlation_final']:.3f}")
    print(f"🚀 Ganho correlação: {results['correlation_gain']:.3f}")
    print(f"⚛️ Fidelidade: {results['fidelity']:.6f}")
    print(f"🌀 Coerência: {results['coherence']:.6f}")
    print(f"🏆 CFC Score: {results['cfc_score']:.6f}")
    print(f"⏱️ Tempo: {results['processing_time_ms']:.1f}ms")
    print(f"✔️ Convergiu: {results['converged']}")
    print("=" * 60)


if __name__ == "__main__":
    demo_kalman_adaptive()
