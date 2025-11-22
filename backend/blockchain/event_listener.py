#!/usr/bin/env python3
"""
Blockchain Event Listener - WebSocket Real-time Events

Escuta eventos do smart contract PoSE Voting em tempo real via WebSocket:
- ProposalCreated: Nova proposta submetida
- VoteCast: Voto registrado
- ProposalApproved: Proposta aprovada
- ProposalRejected: Proposta rejeitada
- ProposalExecuted: Proposta executada

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import asyncio
import json
import logging
from typing import Dict, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Web3.py para eventos
try:
    from web3 import Web3
    from web3.providers.websocket import WebsocketProvider
    from web3.contract import Contract
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos blockchain"""
    PROPOSAL_CREATED = "ProposalCreated"
    VOTE_CAST = "VoteCast"
    PROPOSAL_APPROVED = "ProposalApproved"
    PROPOSAL_REJECTED = "ProposalRejected"
    PROPOSAL_EXECUTED = "ProposalExecuted"


@dataclass
class BlockchainEvent:
    """Evento blockchain"""
    event_type: EventType
    proposal_id: int
    block_number: int
    transaction_hash: str
    data: Dict  # event.args


class BlockchainEventListener:
    """
    Listener WebSocket para eventos do PoSE Voting contract

    Usa Web3.py event filters com WebSocket provider para
    monitoramento em tempo real.
    """

    def __init__(
        self,
        ws_url: str = "ws://localhost:8546",
        contract_address: Optional[str] = None,
        mock_mode: bool = True
    ):
        self.ws_url = ws_url
        self.contract_address = contract_address
        self.mock_mode = mock_mode

        # Event handlers
        self.handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }

        # Web3 setup
        if not self.mock_mode:
            if not WEB3_AVAILABLE:
                raise ImportError("web3 not installed. Install with: pip install web3")

            self.w3 = Web3(WebsocketProvider(self.ws_url))

            # Carrega ABI
            abi_path = Path(__file__).parent / "abi" / "PoSEVoting.json"
            if abi_path.exists():
                with open(abi_path) as f:
                    contract_abi = json.load(f)
                self.contract: Contract = self.w3.eth.contract(
                    address=self.contract_address,
                    abi=contract_abi
                )
            else:
                raise FileNotFoundError(f"Contract ABI not found: {abi_path}")

        # Mock event queue
        self.mock_events: List[BlockchainEvent] = []
        self.running = False

    def on(self, event_type: EventType, handler: Callable[[BlockchainEvent], None]):
        """
        Registra handler para tipo de evento

        Args:
            event_type: Tipo de evento
            handler: Função callback (event: BlockchainEvent) -> None
        """
        self.handlers[event_type].append(handler)

    async def start(self):
        """Inicia listener de eventos"""
        logger.info(f"Iniciando event listener (mock_mode={self.mock_mode})")
        self.running = True

        if self.mock_mode:
            await self._mock_event_loop()
        else:
            await self._real_event_loop()

    def stop(self):
        """Para listener"""
        logger.info("Parando event listener")
        self.running = False

    async def _real_event_loop(self):
        """Loop real de eventos via WebSocket"""
        # Cria event filters
        proposal_created_filter = self.contract.events.ProposalCreated.create_filter(
            fromBlock='latest'
        )
        vote_cast_filter = self.contract.events.VoteCast.create_filter(
            fromBlock='latest'
        )
        proposal_approved_filter = self.contract.events.ProposalApproved.create_filter(
            fromBlock='latest'
        )
        proposal_rejected_filter = self.contract.events.ProposalRejected.create_filter(
            fromBlock='latest'
        )
        proposal_executed_filter = self.contract.events.ProposalExecuted.create_filter(
            fromBlock='latest'
        )

        logger.info("Event filters criados. Aguardando eventos...")

        while self.running:
            try:
                # Poll eventos (Web3.py não suporta async ainda para filters)
                await asyncio.sleep(1)

                # ProposalCreated
                for event in proposal_created_filter.get_new_entries():
                    await self._handle_event(EventType.PROPOSAL_CREATED, event)

                # VoteCast
                for event in vote_cast_filter.get_new_entries():
                    await self._handle_event(EventType.VOTE_CAST, event)

                # ProposalApproved
                for event in proposal_approved_filter.get_new_entries():
                    await self._handle_event(EventType.PROPOSAL_APPROVED, event)

                # ProposalRejected
                for event in proposal_rejected_filter.get_new_entries():
                    await self._handle_event(EventType.PROPOSAL_REJECTED, event)

                # ProposalExecuted
                for event in proposal_executed_filter.get_new_entries():
                    await self._handle_event(EventType.PROPOSAL_EXECUTED, event)

            except Exception as e:
                logger.error(f"Erro no event loop: {e}")
                await asyncio.sleep(5)

    async def _handle_event(self, event_type: EventType, raw_event):
        """Processa evento e chama handlers"""
        blockchain_event = BlockchainEvent(
            event_type=event_type,
            proposal_id=raw_event['args'].get('proposalId', 0),
            block_number=raw_event['blockNumber'],
            transaction_hash=raw_event['transactionHash'].hex(),
            data=dict(raw_event['args'])
        )

        logger.info(
            f"🔔 Evento: {event_type.value} | "
            f"Proposal #{blockchain_event.proposal_id} | "
            f"Block {blockchain_event.block_number}"
        )

        # Chama handlers registrados
        for handler in self.handlers[event_type]:
            try:
                # Handlers podem ser sync ou async
                if asyncio.iscoroutinefunction(handler):
                    await handler(blockchain_event)
                else:
                    handler(blockchain_event)
            except Exception as e:
                logger.error(f"Erro em handler: {e}")

    async def _mock_event_loop(self):
        """Loop mock para testes"""
        logger.info("Mock event loop iniciado")

        while self.running:
            await asyncio.sleep(2)

            # Processa eventos mock
            if self.mock_events:
                event = self.mock_events.pop(0)
                await self._handle_event(event.event_type, {
                    'args': event.data,
                    'blockNumber': event.block_number,
                    'transactionHash': bytes.fromhex(event.transaction_hash[2:])
                })

    def _mock_emit(self, event: BlockchainEvent):
        """Emite evento mock (para testes)"""
        if self.mock_mode:
            self.mock_events.append(event)


# === DEMO ===

async def demo_event_listener():
    """Demonstração do event listener"""
    print("=" * 80)
    print("📡 BLOCKCHAIN EVENT LISTENER - DEMONSTRAÇÃO")
    print("=" * 80)

    listener = BlockchainEventListener(mock_mode=True)

    # Registra handlers
    def on_proposal_created(event: BlockchainEvent):
        print(f"\n🆕 ProposalCreated:")
        print(f"   Proposal ID: #{event.proposal_id}")
        print(f"   Proposer: {event.data.get('proposer', 'N/A')}")
        print(f"   Action: {event.data.get('actionType', 'N/A')}")
        print(f"   Omega Score: {event.data.get('omegaScore', 0) / 1000:.3f}")

    def on_vote_cast(event: BlockchainEvent):
        print(f"\n🗳️  VoteCast:")
        print(f"   Proposal ID: #{event.proposal_id}")
        print(f"   Voter: {event.data.get('voter', 'N/A')}")
        print(f"   Support: {event.data.get('support', False)}")
        print(f"   Weight: {event.data.get('weight', 0)}")

    async def on_proposal_approved(event: BlockchainEvent):
        print(f"\n✅ ProposalApproved:")
        print(f"   Proposal ID: #{event.proposal_id}")
        print(f"   Votes For: {event.data.get('votesFor', 0)}")
        print(f"   Votes Against: {event.data.get('votesAgainst', 0)}")
        print(f"   🚀 EXECUTANDO AÇÃO...")

    listener.on(EventType.PROPOSAL_CREATED, on_proposal_created)
    listener.on(EventType.VOTE_CAST, on_vote_cast)
    listener.on(EventType.PROPOSAL_APPROVED, on_proposal_approved)

    # Inicia listener em background
    listener_task = asyncio.create_task(listener.start())

    # Simula eventos
    await asyncio.sleep(1)

    print("\n📤 Emitindo eventos mock...")

    listener._mock_emit(BlockchainEvent(
        event_type=EventType.PROPOSAL_CREATED,
        proposal_id=1,
        block_number=12345,
        transaction_hash="0xabcd1234",
        data={
            'proposalId': 1,
            'proposer': '0xProposer123',
            'actionType': 0,  # SCALE_UP
            'omegaScore': 920,
            'deadline': 1234567890
        }
    ))

    await asyncio.sleep(2)

    listener._mock_emit(BlockchainEvent(
        event_type=EventType.VOTE_CAST,
        proposal_id=1,
        block_number=12346,
        transaction_hash="0xabcd1235",
        data={
            'proposalId': 1,
            'voter': '0xVoter456',
            'support': True,
            'weight': 1000
        }
    ))

    await asyncio.sleep(2)

    listener._mock_emit(BlockchainEvent(
        event_type=EventType.PROPOSAL_APPROVED,
        proposal_id=1,
        block_number=12347,
        transaction_hash="0xabcd1236",
        data={
            'proposalId': 1,
            'votesFor': 6700,
            'votesAgainst': 1000
        }
    ))

    await asyncio.sleep(2)

    # Para listener
    listener.stop()
    await listener_task

    print("\n" + "=" * 80)
    print("✅ Demonstração concluída!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo_event_listener())
