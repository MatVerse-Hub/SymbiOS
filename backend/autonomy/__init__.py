"""
MatVerse Autonomy Module - Zero Touch Operations

Este módulo implementa autonomia completa para o MatVerse Ω-S:
- Loop OODA fechado em <200ms
- Auto-escala baseada em Kalman CFC
- Decisões autônomas sem intervenção humana

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

from .kalman_policy import KalmanPolicyPredictor
from .metrics_collector import MetricsCollector
from .decision_engine import DecisionEngine
from .actuator import K8sActuator

__all__ = [
    'KalmanPolicyPredictor',
    'MetricsCollector',
    'DecisionEngine',
    'K8sActuator',
]

__version__ = '1.0.0'
