"""
MatVerse Blockchain Integration

Componentes:
- PoSE Voting Smart Contract (Solidity)
- Web3 interface para votação on-chain
- Event listener para decisões aprovadas

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

from .pose_client import PoSEClient, ActionType, ProposalStatus

__all__ = [
    'PoSEClient',
    'ActionType',
    'ProposalStatus',
]

__version__ = '1.0.0'
