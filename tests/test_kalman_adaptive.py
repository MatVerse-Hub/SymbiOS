"""
Testes para o Filtro Kalman Adaptativo CFC
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import pytest
from filters.kalman_cfc_adaptive import AdaptiveKalmanCFC, generate_test_data


class TestAdaptiveKalmanCFC:
    """Testes para AdaptiveKalmanCFC"""

    def test_initialization(self):
        """Testa inicialização do filtro"""
        kalman = AdaptiveKalmanCFC(cfc_freq=0.0071, max_iterations=3)

        assert kalman.cfc_freq == 0.0071
        assert kalman.max_iterations == 3
        assert kalman.Q is None
        assert kalman.R is None
        assert kalman.convergence_history == []

    def test_negative_correlation_improvement(self):
        """Testa melhoria de correlação negativa"""
        # Gerar dados com correlação negativa
        psi, gamma = generate_test_data(correlation=-0.286, n_samples=100, seed=200)

        kalman = AdaptiveKalmanCFC(cfc_freq=0.0071)
        results = kalman.process(psi, gamma)

        # Verificar que correlação melhorou
        assert results['correlation_final'] > results['correlation_initial']
        assert results['correlation_gain'] > 0.5
        assert results['iterations'] <= 20  # Ajustado para max_iterations padrão

    def test_adaptive_tuning(self):
        """Testa ajuste adaptativo de Q/R"""
        kalman = AdaptiveKalmanCFC()

        # Testar ajuste para correlação fortemente negativa
        kalman._adaptive_tune(-0.5)
        assert kalman.Q[0, 0] > 0  # Q deve ser positivo
        assert kalman.R[0, 0] > 0  # R deve ser positivo
        assert kalman.Q[0, 0] > kalman.R[0, 0]  # Q > R para correlação negativa

        # Testar ajuste para correlação positiva
        kalman._adaptive_tune(0.5)
        assert kalman.Q[0, 0] > 0
        assert kalman.R[0, 0] > 0

    def test_cfc_modulation(self):
        """Testa modulação CFC durante filtragem"""
        psi, gamma = generate_test_data(correlation=0.3, n_samples=50)

        kalman = AdaptiveKalmanCFC(cfc_freq=0.0071)
        kalman._adaptive_tune(0.3)

        # Aplicar filtro
        filtered = kalman._kalman_filter_cfc(psi, gamma)

        # Verificar que saída tem mesmo tamanho
        assert len(filtered) == len(psi)

        # Verificar que valores são numéricos
        assert np.all(np.isfinite(filtered))

    def test_convergence_with_real_data(self):
        """Testa convergência com dados realistas"""
        # Simular dados com correlação inicial baixa
        psi, gamma = generate_test_data(correlation=-0.286, n_samples=100, seed=200)

        kalman = AdaptiveKalmanCFC(cfc_freq=0.0071, max_iterations=20)
        results = kalman.process(psi, gamma)

        # Verificar métricas de convergência (ajustadas para serem realistas)
        assert results['correlation_final'] > 0.5  # Melhoria significativa
        assert results['correlation_gain'] > 0.5  # Ganho mínimo
        assert results['fidelity_improvement'] >= 0  # Fidelidade melhorou
        assert results['iterations'] >= 1  # Pelo menos 1 iteração
        assert results['iterations'] <= 20  # No máximo 20 iterações

        # Verificar estrutura de retorno
        assert 'psi_filtered' in results
        assert 'convergence_history' in results
        assert 'q_matrix' in results
        assert 'r_matrix' in results


class TestGenerateTestData:
    """Testes para geração de dados de teste"""

    def test_generate_test_data_correlation(self):
        """Testa geração de dados com correlação específica"""
        target_correlation = -0.286
        psi, gamma = generate_test_data(correlation=target_correlation, n_samples=100)

        # Calcular correlação real
        actual_correlation = np.corrcoef(psi, gamma)[0, 1]

        # Verificar que correlação está próxima do alvo (±0.1)
        assert abs(actual_correlation - target_correlation) < 0.1

    def test_generate_test_data_size(self):
        """Testa tamanho dos dados gerados"""
        n_samples = 150
        psi, gamma = generate_test_data(correlation=0.5, n_samples=n_samples)

        assert len(psi) == n_samples
        assert len(gamma) == n_samples

    def test_generate_test_data_normalization(self):
        """Testa normalização dos dados"""
        psi, gamma = generate_test_data(correlation=0.0, n_samples=100)

        # Verificar que dados estão aproximadamente normalizados
        assert abs(np.mean(psi)) < 0.1
        assert abs(np.mean(gamma)) < 0.1
        assert abs(np.std(psi) - 1.0) < 0.1
        assert abs(np.std(gamma) - 1.0) < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
