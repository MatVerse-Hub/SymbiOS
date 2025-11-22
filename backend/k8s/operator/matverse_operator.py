#!/usr/bin/env python3
"""
MatVerse Kubernetes Operator

Operator kopf para gerenciar autonomia MatVerse via CRD MatVerseScaling.

Features:
- Reconcile loop para decisões autônomas
- Integração com blockchain voting
- Atualização de status do CR
- Event sourcing para auditoria

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import sys
from pathlib import Path
import kopf
import kubernetes
from kubernetes import client, config
from typing import Dict, Any, Optional
import logging
import asyncio
from datetime import datetime, timezone

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from autonomy.metrics_collector import MatVerseMetricsCollector
from autonomy.blockchain_integration import BlockchainDecisionEngine
from blockchain.pose_client import PoSEClient
from autonomy.actuator import K8sActuator
from autonomy.kalman_policy import Action
from autonomy.decision_engine import DecisionMode

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('matverse-operator')


# === GLOBAL STATE ===

# Engines por CR (namespace/name)
engines: Dict[str, BlockchainDecisionEngine] = {}
collectors: Dict[str, MatVerseMetricsCollector] = {}
actuators: Dict[str, K8sActuator] = {}


# === HELPERS ===

def get_k8s_client():
    """Obtém cliente Kubernetes"""
    try:
        config.load_incluster_config()
    except kubernetes.config.ConfigException:
        config.load_kube_config()

    return client.AppsV1Api()


def get_cr_key(namespace: str, name: str) -> str:
    """Gera chave única para CR"""
    return f"{namespace}/{name}"


def parse_decision_mode(mode_str: str) -> DecisionMode:
    """Converte string para DecisionMode"""
    mode_map = {
        'conservative': DecisionMode.CONSERVATIVE,
        'balanced': DecisionMode.BALANCED,
        'aggressive': DecisionMode.AGGRESSIVE,
    }
    return mode_map.get(mode_str.lower(), DecisionMode.BALANCED)


# === OPERATOR HANDLERS ===

@kopf.on.create('matverse.io', 'v1alpha1', 'matversescalings')
def create_fn(spec, name, namespace, logger, **kwargs):
    """
    Handler quando MatVerseScaling CR é criado

    Inicializa:
    - MetricsCollector
    - BlockchainDecisionEngine
    - K8sActuator
    """
    logger.info(f"MatVerseScaling criado: {namespace}/{name}")

    cr_key = get_cr_key(namespace, name)

    # Extrai configuração
    target_ref = spec['targetRef']
    target_name = target_ref['name']
    target_kind = target_ref.get('kind', 'Deployment')

    min_replicas = spec.get('minReplicas', 1)
    max_replicas = spec.get('maxReplicas', 10)

    mode = parse_decision_mode(spec.get('mode', 'balanced'))

    blockchain_config = spec.get('blockchain', {})
    blockchain_enabled = blockchain_config.get('enabled', True)

    # Inicializa componentes
    collector = MatVerseMetricsCollector(collection_interval=10.0)
    collector.start_auto_collection()

    actuator = K8sActuator(
        namespace=namespace,
        deployment_name=target_name,
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        mock_mode=False  # Produção
    )

    # Blockchain (se habilitado)
    if blockchain_enabled:
        rpc_url = blockchain_config.get('rpcUrl', 'http://localhost:8545')
        contract_address = blockchain_config.get('contractAddress')
        require_approval = blockchain_config.get('requireApproval', True)
        voting_timeout = blockchain_config.get('votingTimeout', 120)

        pose_client = PoSEClient(
            rpc_url=rpc_url,
            contract_address=contract_address,
            mock_mode=(contract_address is None)
        )

        engine = BlockchainDecisionEngine(
            metrics_collector=collector,
            pose_client=pose_client,
            k8s_actuator=actuator,
            require_blockchain_approval=require_approval,
            voting_timeout=voting_timeout,
            mode=mode,
            decision_interval=30.0  # 30s
        )
    else:
        # Sem blockchain: usa DecisionEngine simples
        from autonomy.decision_engine import DecisionEngine

        engine = DecisionEngine(
            metrics_collector=collector,
            mode=mode,
            decision_interval=30.0
        )

        # Callback para executar ações
        def execute_action_callback(decision):
            actuator.execute_action(decision.action)

        for action in Action:
            engine.register_action_callback(action, execute_action_callback)

    # Armazena estado global
    engines[cr_key] = engine
    collectors[cr_key] = collector
    actuators[cr_key] = actuator

    # Inicia loop autônomo
    engine.start_autonomous_loop()

    logger.info(f"Engine iniciado para {cr_key} (mode={mode.name}, blockchain={blockchain_enabled})")

    return {
        'status': 'initialized',
        'target': target_name,
        'mode': mode.name,
        'blockchain_enabled': blockchain_enabled
    }


@kopf.on.delete('matverse.io', 'v1alpha1', 'matversescalings')
def delete_fn(spec, name, namespace, logger, **kwargs):
    """Handler quando MatVerseScaling CR é deletado"""
    logger.info(f"MatVerseScaling deletado: {namespace}/{name}")

    cr_key = get_cr_key(namespace, name)

    # Para engine
    if cr_key in engines:
        engines[cr_key].stop_autonomous_loop()
        del engines[cr_key]

    # Para collector
    if cr_key in collectors:
        collectors[cr_key].stop_auto_collection()
        del collectors[cr_key]

    # Remove actuator
    if cr_key in actuators:
        del actuators[cr_key]

    logger.info(f"Recursos liberados para {cr_key}")


@kopf.on.field('matverse.io', 'v1alpha1', 'matversescalings', field='spec.mode')
def mode_changed(old, new, name, namespace, logger, **kwargs):
    """Handler quando mode é alterado"""
    logger.info(f"Mode alterado: {namespace}/{name}: {old} → {new}")

    cr_key = get_cr_key(namespace, name)

    if cr_key in engines:
        new_mode = parse_decision_mode(new)
        engines[cr_key].mode = new_mode
        logger.info(f"Mode atualizado para {new_mode.name}")


@kopf.timer('matverse.io', 'v1alpha1', 'matversescalings', interval=30.0)
async def update_status(spec, status, name, namespace, logger, **kwargs):
    """
    Timer periódico para atualizar status do CR

    Atualiza:
    - currentReplicas / desiredReplicas
    - lastDecision
    - currentMetrics
    - conditions
    """
    cr_key = get_cr_key(namespace, name)

    if cr_key not in engines:
        return

    engine = engines[cr_key]
    collector = collectors[cr_key]
    actuator = actuators[cr_key]

    # Métricas atuais
    omega = collector.get_current_value("omega_score_current", default=0.0)
    psi = collector.get_current_value("psi_index_current", default=0.0)
    beta = collector.get_current_value("beta_antifragile_current", default=0.0)
    cpu = collector.get_current_value("system_cpu_usage", default=0.0)
    latency = collector.get_current_value("latency_ms", default=0.0)

    # Última decisão
    last_decision = engine.get_last_decision()

    # Monta patch de status
    new_status = {
        'currentReplicas': actuator.current_replicas,
        'desiredReplicas': actuator.current_replicas,
        'currentMetrics': {
            'omegaScore': round(omega, 3),
            'psiIndex': round(psi, 3),
            'betaAntifragile': round(beta, 3),
            'cpuUsage': round(cpu, 3),
            'latency': round(latency, 1),
        },
        'conditions': [
            {
                'type': 'Ready',
                'status': 'True',
                'lastTransitionTime': datetime.now(timezone.utc).isoformat(),
                'reason': 'EngineRunning',
                'message': f'Autonomous engine running in {engine.mode.name} mode'
            }
        ]
    }

    if last_decision:
        new_status['lastDecision'] = {
            'action': last_decision.action.value,
            'timestamp': last_decision.timestamp,
            'confidence': round(last_decision.confidence, 3),
            'reasoning': last_decision.reasoning,
        }

        # Se tem blockchain decision
        if hasattr(engine, 'blockchain_decisions') and engine.blockchain_decisions:
            last_bc = engine.blockchain_decisions[-1]
            new_status['lastDecision']['proposalId'] = last_bc.proposal_id
            new_status['lastDecision']['approved'] = last_bc.blockchain_approved

    # Patch status do CR
    api = kubernetes.client.CustomObjectsApi()

    try:
        api.patch_namespaced_custom_object_status(
            group="matverse.io",
            version="v1alpha1",
            namespace=namespace,
            plural="matversescalings",
            name=name,
            body={"status": new_status}
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")


# === MAIN ===

if __name__ == '__main__':
    logger.info("Iniciando MatVerse Operator...")
    kopf.run()
