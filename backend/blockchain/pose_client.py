#!/usr/bin/env python3
"""
PoSE Client - Web3 Interface for Voting Contract

Integra o MatVerse com o smart contract PoSE Voting na blockchain.

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import json
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Web3.py será usado em produção
# Para desenvolvimento, usamos mock
MOCK_MODE = True

if not MOCK_MODE:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware


class ActionType(Enum):
    """Tipos de ação autônoma"""
    SCALE_UP = 0
    SCALE_DOWN = 1
    RETUNE = 2
    ROLLBACK = 3
    EMERGENCY_STOP = 4


class ProposalStatus(Enum):
    """Status de proposta"""
    PENDING = 0
    APPROVED = 1
    REJECTED = 2
    EXECUTED = 3
    EXPIRED = 4


@dataclass
class Proposal:
    """Proposta de ação autônoma"""
    id: int
    proposer: str
    action_type: ActionType
    action_data: bytes

    votes_for: int
    votes_against: int

    created_at: int
    deadline: int

    status: ProposalStatus

    omega_score: int      # * 1000
    psi_index: int        # * 1000
    beta_antifragile: int # * 1000


@dataclass
class VoteResult:
    """Resultado de votação"""
    proposal_id: int
    success: bool
    tx_hash: Optional[str]
    error: Optional[str]


class PoSEClient:
    """
    Cliente Web3 para interagir com o contrato PoSE Voting

    Permite:
    - Submeter propostas de ações autônomas
    - Votar em propostas
    - Consultar status de propostas
    - Escutar eventos de aprovação
    """

    def __init__(
        self,
        rpc_url: str = "http://localhost:8545",
        contract_address: Optional[str] = None,
        private_key: Optional[str] = None,
        mock_mode: bool = MOCK_MODE,
        voting_period: int = 120
    ):
        self.mock_mode = mock_mode
        self.rpc_url = rpc_url
        self.contract_address = contract_address or "0x0000000000000000000000000000000000000000"
        self.private_key = private_key
        self.voting_period = voting_period

        # Estado mock
        self.mock_proposals: Dict[int, Proposal] = {}
        self.mock_proposal_counter = 0
        self.mock_stakes: Dict[str, int] = {}
        self.mock_total_staked = 1000000  # 1M tokens

        if not self.mock_mode:
            self._init_web3()

    def _init_web3(self):
        """Inicializa conexão Web3"""
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Carrega ABI do contrato
        abi_path = Path(__file__).parent / "abi" / "PoSEVoting.json"
        if abi_path.exists():
            with open(abi_path) as f:
                contract_abi = json.load(f)
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=contract_abi
            )
        else:
            raise FileNotFoundError(f"Contract ABI not found: {abi_path}")

        # Account
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
        else:
            self.account = None

    def propose(
        self,
        action_type: ActionType,
        action_data: Dict,
        omega_score: float,
        psi_index: float,
        beta_antifragile: float
    ) -> int:
        """
        Submete proposta de ação autônoma

        Args:
            action_type: Tipo de ação
            action_data: Dados da ação (dict)
            omega_score: Ω-Score atual (0-1)
            psi_index: Ψ-Index atual (0-1)
            beta_antifragile: β atual (0-2)

        Returns:
            proposal_id: ID da proposta criada
        """
        # Converte scores para inteiros (* 1000)
        omega_int = int(omega_score * 1000)
        psi_int = int(psi_index * 1000)
        beta_int = int(beta_antifragile * 1000)

        if self.mock_mode:
            return self._mock_propose(
                action_type, action_data,
                omega_int, psi_int, beta_int
            )

        # Codifica action_data
        action_bytes = json.dumps(action_data).encode()

        # Envia transação
        tx = self.contract.functions.propose(
            action_type.value,
            action_bytes,
            omega_int,
            psi_int,
            beta_int
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Aguarda confirmação
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Extrai proposal_id do evento
        logs = self.contract.events.ProposalCreated().process_receipt(receipt)
        proposal_id = logs[0]['args']['proposalId']

        return proposal_id

    def _mock_propose(
        self,
        action_type: ActionType,
        action_data: Dict,
        omega_int: int,
        psi_int: int,
        beta_int: int
    ) -> int:
        """Mock: Cria proposta"""
        proposal_id = self.mock_proposal_counter + 1
        self.mock_proposal_counter = proposal_id

        proposal = Proposal(
            id=proposal_id,
            proposer="0xMockProposer",
            action_type=action_type,
            action_data=json.dumps(action_data).encode(),
            votes_for=0,
            votes_against=0,
            created_at=int(time.time()),
            deadline=int(time.time()) + self.voting_period,
            status=ProposalStatus.PENDING,
            omega_score=omega_int,
            psi_index=psi_int,
            beta_antifragile=beta_int
        )

        self.mock_proposals[proposal_id] = proposal

        return proposal_id

    def vote(self, proposal_id: int, support: bool) -> VoteResult:
        """
        Vota em uma proposta

        Args:
            proposal_id: ID da proposta
            support: True para apoiar, False para rejeitar

        Returns:
            VoteResult com resultado da votação
        """
        if self.mock_mode:
            return self._mock_vote(proposal_id, support)

        try:
            tx = self.contract.functions.vote(
                proposal_id,
                support
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
            })

            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return VoteResult(
                proposal_id=proposal_id,
                success=True,
                tx_hash=tx_hash.hex(),
                error=None
            )

        except Exception as e:
            return VoteResult(
                proposal_id=proposal_id,
                success=False,
                tx_hash=None,
                error=str(e)
            )

    def _mock_vote(self, proposal_id: int, support: bool) -> VoteResult:
        """Mock: Vota em proposta"""
        if proposal_id not in self.mock_proposals:
            return VoteResult(
                proposal_id=proposal_id,
                success=False,
                tx_hash=None,
                error="Proposal not found"
            )

        proposal = self.mock_proposals[proposal_id]

        # Simula voto com peso 100
        vote_weight = 100

        if support:
            proposal.votes_for += vote_weight
        else:
            proposal.votes_against += vote_weight

        return VoteResult(
            proposal_id=proposal_id,
            success=True,
            tx_hash="0xMockTxHash",
            error=None
        )

    def finalize(self, proposal_id: int) -> bool:
        """
        Finaliza proposta após período de votação

        Args:
            proposal_id: ID da proposta

        Returns:
            True se finalizada com sucesso
        """
        if self.mock_mode:
            return self._mock_finalize(proposal_id)

        tx = self.contract.functions.finalize(proposal_id).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price,
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return True

    def _mock_finalize(self, proposal_id: int) -> bool:
        """Mock: Finaliza proposta"""
        if proposal_id not in self.mock_proposals:
            return False

        proposal = self.mock_proposals[proposal_id]

        # Simula quorum de 67%
        total_votes = proposal.votes_for + proposal.votes_against
        required_quorum = int(self.mock_total_staked * 0.67)

        if total_votes < required_quorum:
            proposal.status = ProposalStatus.EXPIRED
            return True

        if proposal.votes_for > proposal.votes_against:
            proposal.status = ProposalStatus.APPROVED
        else:
            proposal.status = ProposalStatus.REJECTED

        return True

    def get_proposal(self, proposal_id: int) -> Optional[Proposal]:
        """Obtém detalhes de uma proposta"""
        if self.mock_mode:
            return self.mock_proposals.get(proposal_id)

        result = self.contract.functions.getProposal(proposal_id).call()

        return Proposal(
            id=result[0],
            proposer=result[1],
            action_type=ActionType(result[2]),
            action_data=result[3],
            votes_for=result[4],
            votes_against=result[5],
            created_at=result[6],
            deadline=result[7],
            status=ProposalStatus(result[8]),
            omega_score=result[9],
            psi_index=result[10],
            beta_antifragile=result[11]
        )

    def is_approved(self, proposal_id: int) -> bool:
        """Verifica se proposta foi aprovada"""
        proposal = self.get_proposal(proposal_id)
        return proposal and proposal.status == ProposalStatus.APPROVED

    def get_voting_power(self, address: str) -> int:
        """Obtém poder de voto de um endereço"""
        if self.mock_mode:
            return self.mock_stakes.get(address, 0)

        return self.contract.functions.getVotingPower(address).call()


# === DEMO ===

def demo_pose_client():
    """Demonstração do PoSEClient"""
    print("=" * 80)
    print("⛓️  POSE CLIENT - DEMONSTRAÇÃO")
    print("=" * 80)

    client = PoSEClient(mock_mode=True)

    print("\n📝 Criando proposta de SCALE_UP...")
    proposal_id = client.propose(
        action_type=ActionType.SCALE_UP,
        action_data={'replicas': 5, 'reason': 'High CPU usage'},
        omega_score=0.92,
        psi_index=0.95,
        beta_antifragile=1.15
    )
    print(f"   ✅ Proposta criada: ID={proposal_id}")

    print(f"\n🗳️  Votando na proposta {proposal_id}...")
    vote_result = client.vote(proposal_id, support=True)
    print(f"   ✅ Voto registrado: success={vote_result.success}")

    # Simula mais votos
    for i in range(5):
        client._mock_vote(proposal_id, support=True)

    print(f"\n⏰ Finalizando proposta {proposal_id}...")
    finalized = client.finalize(proposal_id)
    print(f"   ✅ Finalizada: {finalized}")

    proposal = client.get_proposal(proposal_id)
    print(f"\n📊 Status da proposta:")
    print(f"   Status: {proposal.status.name}")
    print(f"   Votos a favor: {proposal.votes_for}")
    print(f"   Votos contra: {proposal.votes_against}")
    print(f"   Aprovada: {client.is_approved(proposal_id)}")

    print("\n" + "=" * 80)
    print("✅ Demonstração concluída!")
    print("=" * 80)


if __name__ == "__main__":
    demo_pose_client()
