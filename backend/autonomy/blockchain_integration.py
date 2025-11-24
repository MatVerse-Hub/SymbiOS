#!/usr/bin/env python3
"""
Blockchain Integration - DecisionEngine + PoSE Voting

Integra decisões autônomas com votação on-chain para governança
descentralizada do MatVerse.

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import sys
from pathlib import Path
import time
from typing import Optional, Dict, List
from dataclasses import dataclass
import threading
from threading import Thread

# Adiciona blockchain ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from blockchain.pose_client import PoSEClient, ActionType as BCActionType, ProposalStatus
from autonomy.decision_engine import DecisionEngine, Decision
from autonomy.kalman_policy import Action
from autonomy.actuator import K8sActuator


# Mapeamento de ações
ACTION_TO_BC_TYPE = {
    Action.SCALE_UP: BCActionType.SCALE_UP,
    Action.SCALE_DOWN: BCActionType.SCALE_DOWN,
    Action.RETUNE: BCActionType.RETUNE,
    Action.ROLLBACK: BCActionType.ROLLBACK,
}


@dataclass
class BlockchainDecision:
    """Decisão com contexto blockchain"""
    decision: Decision
    proposal_id: Optional[int]
    blockchain_approved: bool
    execution_blocked: bool


class BlockchainDecisionEngine(DecisionEngine):
    """
    Decision Engine com integração blockchain

    Workflow:
    1. DecisionEngine faz decisão (Loop OODA)
    2. Se ação != NOOP, submete proposta on-chain
    3. Aguarda votação (ou timeout)
    4. Se aprovada, executa ação via K8sActuator
    5. Marca proposta como executed on-chain
    """

    def __init__(
        self,
        metrics_collector,
        pose_client: Optional[PoSEClient] = None,
        k8s_actuator: Optional[K8sActuator] = None,
        require_blockchain_approval: bool = True,
        voting_timeout: int = 120,  # 2 minutos
        **kwargs
    ):
        super().__init__(metrics_collector, **kwargs)

        self.pose_client = pose_client or PoSEClient(mock_mode=True)
        self.k8s_actuator = k8s_actuator or K8sActuator(mock_mode=True)
        self.require_blockchain_approval = require_blockchain_approval
        self.voting_timeout = voting_timeout

        # Histórico blockchain
        self.blockchain_decisions: List[BlockchainDecision] = []

        # Callback quando proposta é criada
        self.on_proposal_created = None

    def make_blockchain_decision(self) -> BlockchainDecision:
        """
        Faz decisão autônoma + votação blockchain

        Returns:
            BlockchainDecision com proposta e status
        """
        # Passo 1: Decisão local (Loop OODA)
        decision = self.make_decision()

        # Se NOOP, não precisa votação
        if decision.action == Action.NOOP:
            bc_decision = BlockchainDecision(
                decision=decision,
                proposal_id=None,
                blockchain_approved=True,  # NOOP sempre aprovado
                execution_blocked=False
            )
            self.blockchain_decisions.append(bc_decision)
            return bc_decision

        # Passo 2: Submeter proposta on-chain
        proposal_id = None
        blockchain_approved = False

        if self.require_blockchain_approval:
            try:
                proposal_id = self._submit_proposal(decision)

                # Auto-vota a favor (como proposer)
                self.pose_client.vote(proposal_id, support=True)

                # Aguarda votação (timeout)
                blockchain_approved = self._wait_for_approval(proposal_id)

            except Exception as e:
                print(f"❌ Erro blockchain: {e}")
                blockchain_approved = False
        else:
            # Modo bypass: aprova automaticamente
            blockchain_approved = True

        # Passo 3: Executar se aprovado
        execution_blocked = not blockchain_approved

        if blockchain_approved:
            result = self.k8s_actuator.execute_action(decision.action)
            print(f"✅ Ação executada: {result.details}")

            # Marca como executed on-chain
            if proposal_id:
                try:
                    marked = self.pose_client.mark_executed(proposal_id)
                    if marked:
                        print(f"⛓️  Proposta #{proposal_id} marcada como EXECUTED on-chain")
                    else:
                        print(f"⚠️  Falha ao marcar proposta #{proposal_id} como executada")
                except Exception as e:
                    print(f"❌ Erro ao marcar proposta como executada: {e}")

        bc_decision = BlockchainDecision(
            decision=decision,
            proposal_id=proposal_id,
            blockchain_approved=blockchain_approved,
            execution_blocked=execution_blocked
        )

        self.blockchain_decisions.append(bc_decision)
        return bc_decision

    def _submit_proposal(self, decision: Decision) -> int:
        """Submete proposta para votação on-chain"""
        bc_action_type = ACTION_TO_BC_TYPE.get(decision.action)
        if not bc_action_type:
            raise ValueError(f"Ação não mapeada: {decision.action}")

        action_data = {
            'action': decision.action.value,
            'reasoning': decision.reasoning,
            'confidence': decision.confidence,
            'timestamp': decision.timestamp,
        }

        proposal_id = self.pose_client.propose(
            action_type=bc_action_type,
            action_data=action_data,
            omega_score=decision.system_state.omega_score,
            psi_index=decision.system_state.psi_index,
            beta_antifragile=decision.system_state.beta_antifragile
        )

        # Callback quando proposta é criada
        if self.on_proposal_created:
            self.on_proposal_created(proposal_id)

        return proposal_id

    def _wait_for_approval(self, proposal_id: int) -> bool:
        """
        Aguarda aprovação da proposta

        Em produção, usaria event listener WebSocket.
        Aqui usamos polling simples.
        """
        start_time = time.time()

        while time.time() - start_time < self.voting_timeout:
            proposal = self.pose_client.get_proposal(proposal_id)

            # Se ainda pending, aguarda
            if proposal.status == ProposalStatus.PENDING:
                # Tenta finalizar se deadline passou
                if time.time() >= proposal.deadline:
                    self.pose_client.finalize(proposal_id)
                    proposal = self.pose_client.get_proposal(proposal_id)

            # Verifica aprovação
            if proposal.status == ProposalStatus.APPROVED:
                return True
            elif proposal.status in [ProposalStatus.REJECTED, ProposalStatus.EXPIRED]:
                return False

            time.sleep(1)  # Poll a cada 1s

        # Timeout: força finalização
        self.pose_client.finalize(proposal_id)
        return self.pose_client.is_approved(proposal_id)

    def get_blockchain_stats(self) -> Dict:
        """Retorna estatísticas blockchain"""
        if not self.blockchain_decisions:
            return {}

        total = len(self.blockchain_decisions)
        approved = sum(1 for d in self.blockchain_decisions if d.blockchain_approved)
        blocked = sum(1 for d in self.blockchain_decisions if d.execution_blocked)

        proposals_created = sum(1 for d in self.blockchain_decisions if d.proposal_id is not None)

        return {
            'total_decisions': total,
            'blockchain_approved': approved,
            'execution_blocked': blocked,
            'approval_rate': approved / total if total > 0 else 0,
            'proposals_created': proposals_created,
        }


# === DEMO ===

def simulate_external_voters(pose_client: PoSEClient, proposal_id: int, num_votes: int, delay: float = 0.5):
    """Simula votantes externos votando após um delay"""
    def vote_thread():
        time.sleep(delay)
        for _ in range(num_votes):
            pose_client._mock_vote(proposal_id, support=True)

    thread = Thread(target=vote_thread, daemon=True)
    thread.start()


def demo_blockchain_integration():
    """Demonstração da integração blockchain"""
    print("=" * 80)
    print("⛓️  BLOCKCHAIN INTEGRATION - DEMONSTRAÇÃO")
    print("=" * 80)

    from autonomy.metrics_collector import MatVerseMetricsCollector

    # Setup
    collector = MatVerseMetricsCollector()

    # PoSEClient com período de votação curto para demo
    pose_client = PoSEClient(mock_mode=True, voting_period=2)  # 2s voting period

    # Reduz total staked para facilitar atingir quorum na demo
    pose_client.mock_total_staked = 1000  # 1K tokens (vs 1M padrão)

    engine = BlockchainDecisionEngine(
        metrics_collector=collector,
        pose_client=pose_client,
        require_blockchain_approval=True,
        voting_timeout=5  # 5s timeout (> voting_period)
    )

    # Simula votantes externos quando proposta é criada
    def on_proposal(proposal_id):
        simulate_external_voters(pose_client, proposal_id, num_votes=10, delay=0.5)

    engine.on_proposal_created = on_proposal

    # Cenários de teste
    scenarios = [
        ("Normal", 0.95, 0.97, 1.2, 0.45, 50, 1500),
        ("Alta Carga - SCALE_UP", 0.92, 0.95, 1.15, 0.85, 180, 2500),
    ]

    for i, (name, omega, psi, beta, cpu, lat, thr) in enumerate(scenarios):
        print(f"\n{'='*80}")
        print(f"📊 Cenário {i+1}: {name}")
        print(f"   Estado: Ω={omega:.3f}, CPU={cpu:.1%}, Lat={lat:.0f}ms")

        collector.update_matverse_metrics(omega, psi, beta, lat, thr)

        # Atualiza CPU manualmente para o cenário
        collector.record_metric("system_cpu_usage", cpu)

        # Decisão + Blockchain
        bc_decision = engine.make_blockchain_decision()

        print(f"\n   ✅ Decisão: {bc_decision.decision.action.value}")
        print(f"   📈 Confiança: {bc_decision.decision.confidence:.3f}")
        print(f"   💭 Reasoning: {bc_decision.decision.reasoning}")

        if bc_decision.proposal_id:
            print(f"\n   ⛓️  Proposta on-chain: #{bc_decision.proposal_id}")

            proposal = pose_client.get_proposal(bc_decision.proposal_id)
            print(f"   🗳️  Votos: {proposal.votes_for} a favor, {proposal.votes_against} contra")
            print(f"   📊 Status: {proposal.status.name}")

        print(f"\n   {'✅' if bc_decision.blockchain_approved else '❌'} Aprovação blockchain: {bc_decision.blockchain_approved}")
        print(f"   {'🔒' if bc_decision.execution_blocked else '🚀'} Execução: {'BLOQUEADA' if bc_decision.execution_blocked else 'PERMITIDA'}")

    # Estatísticas
    print(f"\n{'='*80}")
    print("📈 Estatísticas Blockchain:")
    stats = engine.get_blockchain_stats()
    print(f"   Total de decisões: {stats['total_decisions']}")
    print(f"   Aprovadas blockchain: {stats['blockchain_approved']}")
    print(f"   Bloqueadas: {stats['execution_blocked']}")
    print(f"   Taxa de aprovação: {stats['approval_rate']:.1%}")
    print(f"   Propostas criadas: {stats['proposals_created']}")

    print("\n" + "=" * 80)
    print("✅ Demonstração concluída!")
    print("=" * 80)


if __name__ == "__main__":
    demo_blockchain_integration()
