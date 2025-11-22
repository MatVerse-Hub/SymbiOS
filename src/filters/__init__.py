"""
Filtros adaptativos para processamento de sinais quântico-clássicos
"""

from .kalman_cfc_adaptive import AdaptiveKalmanCFC, generate_test_data

__all__ = ['AdaptiveKalmanCFC', 'generate_test_data']
