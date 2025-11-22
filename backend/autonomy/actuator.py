#!/usr/bin/env python3
"""
K8s Actuator - Interface de Atuação

Executa ações autônomas no cluster Kubernetes:
- Scale up/down de réplicas
- Rolling updates
- Rollbacks
- Re-tuning de parâmetros

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

from .kalman_policy import Action

# Kubernetes client (opcional)
try:
    from kubernetes import client, config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False


@dataclass
class ActuationResult:
    """Resultado de uma atuação"""
    success: bool
    action: Action
    details: str
    execution_time_ms: float
    timestamp: float


class K8sActuator:
    """
    Actuator para Kubernetes (mock para desenvolvimento)

    Produção: Substituir por cliente real kubernetes.client.AppsV1Api
    """

    def __init__(
        self,
        namespace: str = "default",
        deployment_name: str = "matverse-api",
        mock_mode: bool = True,  # True para testes sem K8s real
        min_replicas: int = 2,
        max_replicas: int = 10
    ):
        self.namespace = namespace
        self.deployment_name = deployment_name
        self.mock_mode = mock_mode
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas

        # Estado simulado (mock)
        self.current_replicas = 3

        # Cliente K8s (se não for mock)
        if not self.mock_mode:
            if not K8S_AVAILABLE:
                raise ImportError("kubernetes library not installed. Install with: pip install kubernetes")

            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()

            self.k8s_apps = client.AppsV1Api()

            # Obtém replicas atuais do deployment
            self._sync_current_replicas()

    def execute_action(self, action: Action) -> ActuationResult:
        """
        Executa uma ação no cluster

        Args:
            action: Ação a executar

        Returns:
            ActuationResult com resultado da execução
        """
        start_time = time.time()

        if action == Action.SCALE_UP:
            result = self._scale_up()
        elif action == Action.SCALE_DOWN:
            result = self._scale_down()
        elif action == Action.RETUNE:
            result = self._retune_parameters()
        elif action == Action.ROLLBACK:
            result = self._rollback_deployment()
        elif action == Action.NOOP:
            result = ActuationResult(
                success=True,
                action=action,
                details="No action required",
                execution_time_ms=0.1,
                timestamp=time.time()
            )
        else:
            result = ActuationResult(
                success=False,
                action=action,
                details=f"Unknown action: {action}",
                execution_time_ms=0.0,
                timestamp=time.time()
            )

        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    def _scale_up(self) -> ActuationResult:
        """Aumenta número de réplicas"""
        if self.current_replicas >= self.max_replicas:
            return ActuationResult(
                success=False,
                action=Action.SCALE_UP,
                details=f"Already at max replicas ({self.max_replicas})",
                execution_time_ms=0.0,
                timestamp=time.time()
            )

        old_replicas = self.current_replicas
        target_replicas = min(self.current_replicas + 2, self.max_replicas)

        if self.mock_mode:
            self.current_replicas = target_replicas
            success = True
        else:
            success = self._scale_deployment_k8s(target_replicas)

        if success:
            return ActuationResult(
                success=True,
                action=Action.SCALE_UP,
                details=f"Scaled {old_replicas} → {self.current_replicas} replicas",
                execution_time_ms=50.0 if self.mock_mode else 200.0,
                timestamp=time.time()
            )
        else:
            return ActuationResult(
                success=False,
                action=Action.SCALE_UP,
                details="Failed to scale deployment",
                execution_time_ms=0.0,
                timestamp=time.time()
            )

    def _scale_down(self) -> ActuationResult:
        """Reduz número de réplicas"""
        if self.current_replicas <= self.min_replicas:
            return ActuationResult(
                success=False,
                action=Action.SCALE_DOWN,
                details=f"Already at min replicas ({self.min_replicas})",
                execution_time_ms=0.0,
                timestamp=time.time()
            )

        old_replicas = self.current_replicas
        target_replicas = max(self.current_replicas - 1, self.min_replicas)

        if self.mock_mode:
            self.current_replicas = target_replicas
            success = True
        else:
            success = self._scale_deployment_k8s(target_replicas)

        if success:
            return ActuationResult(
                success=True,
                action=Action.SCALE_DOWN,
                details=f"Scaled {old_replicas} → {self.current_replicas} replicas",
                execution_time_ms=40.0 if self.mock_mode else 180.0,
                timestamp=time.time()
            )
        else:
            return ActuationResult(
                success=False,
                action=Action.SCALE_DOWN,
                details="Failed to scale deployment",
                execution_time_ms=0.0,
                timestamp=time.time()
            )

    def _retune_parameters(self) -> ActuationResult:
        """Re-ajusta parâmetros do sistema"""
        if self.mock_mode:
            return ActuationResult(
                success=True,
                action=Action.RETUNE,
                details="Parameters retuned: η=0.3→0.4, γ=0.05→0.03",
                execution_time_ms=30.0,
                timestamp=time.time()
            )

        # TODO: Implementar ajuste real de ConfigMaps
        return ActuationResult(
            success=False,
            action=Action.RETUNE,
            details="Parameter tuning not implemented",
            execution_time_ms=0.0,
            timestamp=time.time()
        )

    def _rollback_deployment(self) -> ActuationResult:
        """Faz rollback do deployment"""
        if self.mock_mode:
            return ActuationResult(
                success=True,
                action=Action.ROLLBACK,
                details="Rolled back to previous revision",
                execution_time_ms=120.0,
                timestamp=time.time()
            )

        # TODO: Implementar rollback real
        return ActuationResult(
            success=False,
            action=Action.ROLLBACK,
            details="Rollback not implemented",
            execution_time_ms=0.0,
            timestamp=time.time()
        )

    def _sync_current_replicas(self):
        """Sincroniza current_replicas com deployment real (K8s)"""
        if self.mock_mode:
            return

        try:
            deployment = self.k8s_apps.read_namespaced_deployment(
                name=self.deployment_name,
                namespace=self.namespace
            )
            self.current_replicas = deployment.spec.replicas or 1
        except Exception as e:
            print(f"Erro ao sincronizar replicas: {e}")
            self.current_replicas = 3  # Fallback

    def _scale_deployment_k8s(self, target_replicas: int) -> bool:
        """Escala deployment no K8s real"""
        if self.mock_mode:
            return True

        try:
            # Patch do deployment
            body = {
                "spec": {
                    "replicas": target_replicas
                }
            }

            self.k8s_apps.patch_namespaced_deployment_scale(
                name=self.deployment_name,
                namespace=self.namespace,
                body=body
            )

            self.current_replicas = target_replicas
            return True

        except Exception as e:
            print(f"Erro ao escalar deployment: {e}")
            return False

    def get_current_state(self) -> Dict:
        """Retorna estado atual do cluster"""
        if not self.mock_mode:
            self._sync_current_replicas()

        return {
            'replicas': self.current_replicas,
            'min_replicas': self.min_replicas,
            'max_replicas': self.max_replicas,
            'namespace': self.namespace,
            'deployment': self.deployment_name,
            'mock_mode': self.mock_mode
        }


# === DEMO ===

def demo_actuator():
    """Demonstração do K8sActuator"""
    print("=" * 80)
    print("⚙️  K8S ACTUATOR - DEMONSTRAÇÃO")
    print("=" * 80)

    actuator = K8sActuator(mock_mode=True)

    print(f"\n📊 Estado inicial:")
    state = actuator.get_current_state()
    print(f"   Replicas: {state['replicas']} (min: {state['min_replicas']}, max: {state['max_replicas']})")
    print(f"   Deployment: {state['deployment']} ({state['namespace']})")

    actions_to_test = [
        Action.SCALE_UP,
        Action.SCALE_UP,
        Action.NOOP,
        Action.SCALE_DOWN,
        Action.RETUNE,
        Action.ROLLBACK,
    ]

    for i, action in enumerate(actions_to_test):
        print(f"\n🎯 Teste {i+1}: {action.value}")
        result = actuator.execute_action(action)

        if result.success:
            print(f"   ✅ Sucesso: {result.details}")
        else:
            print(f"   ❌ Falha: {result.details}")

        print(f"   ⏱️  Tempo: {result.execution_time_ms:.1f}ms")

        if action in [Action.SCALE_UP, Action.SCALE_DOWN]:
            state = actuator.get_current_state()
            print(f"   📊 Replicas agora: {state['replicas']}")

    print("\n" + "=" * 80)
    print("✅ Demonstração concluída!")
    print("=" * 80)


if __name__ == "__main__":
    demo_actuator()
