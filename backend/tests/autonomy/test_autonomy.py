#!/usr/bin/env python3
"""
Test Suite - Autonomy Module

Testes completos para o módulo de autonomia do MatVerse:
- KalmanPolicyPredictor
- MetricsCollector
- DecisionEngine
- K8sActuator

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import sys
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import time
import pytest
from autonomy.kalman_policy import (
    KalmanPolicyPredictor,
    SystemState,
    Action,
    PolicyPrediction
)
from autonomy.metrics_collector import (
    MetricsCollector,
    MatVerseMetricsCollector
)
from autonomy.decision_engine import (
    DecisionEngine,
    DecisionMode
)
from autonomy.actuator import K8sActuator


# === TESTES KALMAN POLICY PREDICTOR ===

class TestKalmanPolicyPredictor:
    """Testes do KalmanPolicyPredictor"""

    def test_initialization(self):
        """Testa inicialização do predictor"""
        predictor = KalmanPolicyPredictor()
        assert predictor.state_dim == 5
        assert predictor.target_omega == 0.95
        assert len(predictor.state_history) == 0

    def test_predict_normal_state(self):
        """Testa predição em estado normal"""
        predictor = KalmanPolicyPredictor()
        state = SystemState(0.95, 0.97, 1.2, 0.45, 50, 1500)

        action, prediction = predictor.predict(state)

        assert action == Action.NOOP
        assert 0 <= prediction.confidence <= 1
        assert prediction.processing_time_ms < 10  # Muito rápido

    def test_predict_high_load(self):
        """Testa predição sob alta carga"""
        predictor = KalmanPolicyPredictor()
        state = SystemState(0.92, 0.95, 1.15, 0.85, 180, 2500)

        action, prediction = predictor.predict(state)

        assert action == Action.SCALE_UP
        assert prediction.confidence > 0.70

    def test_predict_low_utilization(self):
        """Testa predição com subutilização"""
        predictor = KalmanPolicyPredictor()
        state = SystemState(0.93, 0.96, 1.18, 0.20, 30, 800)

        action, prediction = predictor.predict(state)

        assert action == Action.SCALE_DOWN
        assert prediction.confidence > 0.50

    def test_predict_critical_omega(self):
        """Testa predição com Ω crítico"""
        predictor = KalmanPolicyPredictor()
        state = SystemState(0.65, 0.70, 0.95, 0.55, 120, 1200)

        action, prediction = predictor.predict(state)

        assert action == Action.ROLLBACK
        assert prediction.confidence > 0.30

    def test_state_history_tracking(self):
        """Testa rastreamento de histórico"""
        predictor = KalmanPolicyPredictor()

        for i in range(10):
            state = SystemState(0.9, 0.95, 1.0 + i*0.01, 0.5, 50, 1000)
            predictor.predict(state)

        assert len(predictor.state_history) == 10

    def test_adaptive_noise(self):
        """Testa adaptação de ruído"""
        predictor = KalmanPolicyPredictor()

        Q_initial = predictor.Q.copy()

        # Força grande inovação
        state = SystemState(0.5, 0.6, 0.8, 0.9, 300, 500)
        predictor.predict(state)

        # Q deve ter mudado
        assert not (predictor.Q == Q_initial).all()


# === TESTES METRICS COLLECTOR ===

class TestMetricsCollector:
    """Testes do MetricsCollector"""

    def test_initialization(self):
        """Testa inicialização"""
        collector = MetricsCollector()
        assert collector.collection_interval == 1.0
        assert len(collector._metrics) == 0

    def test_record_metric(self):
        """Testa gravação de métrica"""
        collector = MetricsCollector()
        collector.record_metric("test_metric", 42.0)

        value = collector.get_current_value("test_metric")
        assert value == 42.0

    def test_record_metric_with_labels(self):
        """Testa métrica com labels"""
        collector = MetricsCollector()
        collector.record_metric("cpu", 0.75, labels={"core": "0"})
        collector.record_metric("cpu", 0.85, labels={"core": "1"})

        cpu0 = collector.get_current_value("cpu", labels={"core": "0"})
        cpu1 = collector.get_current_value("cpu", labels={"core": "1"})

        assert cpu0 == 0.75
        assert cpu1 == 0.85

    def test_metric_history(self):
        """Testa histórico de métricas"""
        collector = MetricsCollector()

        for i in range(10):
            collector.record_metric("counter", float(i))

        history = collector.get_metric_history("counter")
        assert len(history) == 10
        assert history[-1].value == 9.0

    def test_export_prometheus(self):
        """Testa export para Prometheus"""
        collector = MetricsCollector()
        collector.record_metric("omega_score", 0.95, metric_type="gauge")
        collector.record_metric("requests", 1000, metric_type="counter")

        output = collector.export_prometheus()

        assert "omega_score" in output
        assert "requests" in output
        assert "# TYPE" in output
        assert "# HELP" in output

    def test_collect_system_metrics(self):
        """Testa coleta de métricas do sistema"""
        collector = MetricsCollector()
        collector.collect_system_metrics()

        cpu = collector.get_current_value("system_cpu_usage")
        mem = collector.get_current_value("system_memory_usage")

        assert 0 <= cpu <= 1
        assert 0 <= mem <= 1

    def test_auto_collection(self):
        """Testa coleta automática"""
        collector = MetricsCollector(collection_interval=0.1)
        collector.start_auto_collection()

        time.sleep(0.3)

        cpu = collector.get_current_value("system_cpu_usage")
        assert cpu >= 0  # Pelo menos uma coleta deve ter ocorrido

        collector.stop_auto_collection()


class TestMatVerseMetricsCollector:
    """Testes do MatVerseMetricsCollector"""

    def test_initialization_with_matverse_metrics(self):
        """Testa inicialização com métricas MatVerse"""
        collector = MatVerseMetricsCollector()

        omega = collector.get_current_value("omega_score_current")
        quantum_states = collector.get_current_value("quantum_states_count")

        assert omega == 0.0  # Valor inicial
        assert quantum_states == 46080

    def test_update_matverse_metrics(self):
        """Testa atualização de métricas MatVerse"""
        collector = MatVerseMetricsCollector()
        collector.update_matverse_metrics(0.95, 0.97, 1.2, 50.0, 1500.0)

        omega = collector.get_current_value("omega_score_current")
        psi = collector.get_current_value("psi_index_current")
        beta = collector.get_current_value("beta_antifragile_current")

        assert omega == 0.95
        assert psi == 0.97
        assert beta == 1.2


# === TESTES DECISION ENGINE ===

class TestDecisionEngine:
    """Testes do DecisionEngine"""

    def test_initialization(self):
        """Testa inicialização"""
        collector = MatVerseMetricsCollector()
        engine = DecisionEngine(collector)

        assert engine.mode == DecisionMode.BALANCED
        assert engine.min_confidence == 0.70

    def test_make_decision(self):
        """Testa tomada de decisão"""
        collector = MatVerseMetricsCollector()
        collector.update_matverse_metrics(0.95, 0.97, 1.2, 50.0, 1500.0)

        engine = DecisionEngine(collector)
        decision = engine.make_decision()

        assert decision.action in Action
        assert 0 <= decision.confidence <= 1
        assert decision.processing_time_ms < 100  # Target: <50ms

    def test_decision_performance(self):
        """Testa performance do loop OODA"""
        collector = MatVerseMetricsCollector()
        collector.update_matverse_metrics(0.95, 0.97, 1.2, 50.0, 1500.0)

        engine = DecisionEngine(collector)
        decision = engine.make_decision()

        # Targets: Observe <10ms, Orient <50ms, Decide <50ms
        assert decision.observe_time_ms < 10
        assert decision.orient_time_ms < 50
        assert decision.decide_time_ms < 50
        assert decision.processing_time_ms < 200  # Total

    def test_decision_modes(self):
        """Testa diferentes modos de decisão"""
        collector = MatVerseMetricsCollector()
        collector.update_matverse_metrics(0.85, 0.90, 1.1, 0.65, 85.0, 1800.0)

        # Conservative
        engine_conservative = DecisionEngine(collector, mode=DecisionMode.CONSERVATIVE)
        decision_conservative = engine_conservative.make_decision()

        # Aggressive
        engine_aggressive = DecisionEngine(collector, mode=DecisionMode.AGGRESSIVE)
        decision_aggressive = engine_aggressive.make_decision()

        # Aggressive deve ser mais proativo
        # (teste de comportamento, não necessariamente diferente sempre)
        assert decision_conservative.mode == DecisionMode.CONSERVATIVE
        assert decision_aggressive.mode == DecisionMode.AGGRESSIVE

    def test_decision_history(self):
        """Testa histórico de decisões"""
        collector = MatVerseMetricsCollector()
        engine = DecisionEngine(collector)

        for _ in range(5):
            collector.update_matverse_metrics(0.95, 0.97, 1.2, 50.0, 1500.0)
            engine.make_decision()

        history = engine.get_decision_history()
        assert len(history) == 5

    def test_action_callback(self):
        """Testa callbacks de ação"""
        collector = MatVerseMetricsCollector()
        engine = DecisionEngine(collector)

        callback_executed = []

        def test_callback(decision):
            callback_executed.append(decision.action)

        engine.register_action_callback(Action.SCALE_UP, test_callback)

        # Força scale_up (CPU alto)
        collector.update_matverse_metrics(0.92, 0.95, 1.15, 0.85, 180, 2500)
        engine.start_autonomous_loop()

        time.sleep(1.5)  # Aguarda decisão
        engine.stop_autonomous_loop()

        # Pelo menos uma decisão deve ter sido tomada
        assert len(engine.decision_history) > 0


# === TESTES K8S ACTUATOR ===

class TestK8sActuator:
    """Testes do K8sActuator"""

    def test_initialization(self):
        """Testa inicialização"""
        actuator = K8sActuator()
        assert actuator.current_replicas == 3
        assert actuator.mock_mode is True

    def test_scale_up(self):
        """Testa scale up"""
        actuator = K8sActuator()
        initial_replicas = actuator.current_replicas

        result = actuator.execute_action(Action.SCALE_UP)

        assert result.success is True
        assert actuator.current_replicas > initial_replicas

    def test_scale_down(self):
        """Testa scale down"""
        actuator = K8sActuator()
        actuator.current_replicas = 5  # Define alto para permitir scale down

        initial_replicas = actuator.current_replicas
        result = actuator.execute_action(Action.SCALE_DOWN)

        assert result.success is True
        assert actuator.current_replicas < initial_replicas

    def test_scale_up_at_max(self):
        """Testa scale up quando já está no máximo"""
        actuator = K8sActuator()
        actuator.current_replicas = actuator.max_replicas

        result = actuator.execute_action(Action.SCALE_UP)

        assert result.success is False
        assert "max replicas" in result.details

    def test_scale_down_at_min(self):
        """Testa scale down quando já está no mínimo"""
        actuator = K8sActuator()
        actuator.current_replicas = actuator.min_replicas

        result = actuator.execute_action(Action.SCALE_DOWN)

        assert result.success is False
        assert "min replicas" in result.details

    def test_retune(self):
        """Testa re-tuning"""
        actuator = K8sActuator()
        result = actuator.execute_action(Action.RETUNE)

        assert result.success is True
        assert result.action == Action.RETUNE

    def test_rollback(self):
        """Testa rollback"""
        actuator = K8sActuator()
        result = actuator.execute_action(Action.ROLLBACK)

        assert result.success is True
        assert result.action == Action.ROLLBACK

    def test_noop(self):
        """Testa ação NOOP"""
        actuator = K8sActuator()
        result = actuator.execute_action(Action.NOOP)

        assert result.success is True
        assert result.execution_time_ms < 1

    def test_execution_time(self):
        """Testa tempo de execução"""
        actuator = K8sActuator()
        result = actuator.execute_action(Action.SCALE_UP)

        # Mock mode deve ser rápido
        assert result.execution_time_ms < 200


# === TESTES DE INTEGRAÇÃO ===

class TestIntegration:
    """Testes de integração completa"""

    def test_full_autonomy_loop(self):
        """Testa loop completo de autonomia"""
        # Setup
        collector = MatVerseMetricsCollector(collection_interval=0.1)
        collector.start_auto_collection()

        engine = DecisionEngine(collector, decision_interval=0.5)
        actuator = K8sActuator()

        # Callback de atuação
        actions_executed = []

        def on_scale_up(decision):
            result = actuator.execute_action(Action.SCALE_UP)
            actions_executed.append((Action.SCALE_UP, result.success))

        engine.register_action_callback(Action.SCALE_UP, on_scale_up)

        # Força cenário de scale_up
        collector.update_matverse_metrics(0.92, 0.95, 1.15, 0.85, 180, 2500)

        # Inicia loop autônomo
        engine.start_autonomous_loop()

        # Aguarda decisão
        time.sleep(1.0)

        # Para
        engine.stop_autonomous_loop()
        collector.stop_auto_collection()

        # Verificações
        assert len(engine.decision_history) > 0
        last_decision = engine.get_last_decision()
        assert last_decision is not None

    def test_performance_under_load(self):
        """Testa performance sob carga"""
        collector = MatVerseMetricsCollector()
        engine = DecisionEngine(collector)

        # 100 decisões rápidas
        start = time.time()

        for i in range(100):
            omega = 0.90 + (i % 10) / 100
            collector.update_matverse_metrics(omega, 0.95, 1.2, 50.0, 1500.0)
            engine.make_decision()

        elapsed = time.time() - start

        # Deve processar 100 decisões em <1s
        assert elapsed < 1.0

        stats = engine.get_statistics()
        assert stats['avg_processing_time_ms'] < 50


# === RUNNER ===

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
