"""
Sistema PQC (Post-Quantum Cryptography) para MatVerse
Implementação de assinaturas Dilithium3 e evidências criptográficas

Author: MatVerse Team
License: MIT
"""

import hashlib
import json
import base64
from typing import Dict, Tuple, List
from datetime import datetime


class PQCSigner:
    """Sistema PQC (Post-Quantum Cryptography) para MatVerse"""

    def __init__(self, scheme: str = "DILITHIUM3"):
        """
        Inicializa o assinador PQC

        Args:
            scheme: Esquema criptográfico (DILITHIUM3, KYBER1024, etc)
        """
        self.scheme = scheme
        self.keypair = self.generate_keypair()

    def generate_keypair(self) -> Dict:
        """
        Gera par de chaves PQC

        Returns:
            Dict com chaves pública e privada
        """
        # Simulação de geração de chaves Dilithium3
        # Em produção, usar biblioteca pqcrypto ou similar
        seed = hashlib.sha3_256(b'matverse_pqc_seed').hexdigest()
        private_key = f"dilithium3_private_{seed[:32]}"
        public_key = f"dilithium3_public_{hashlib.sha3_256(private_key.encode()).hexdigest()[:32]}"

        return {
            'private_key': private_key,
            'public_key': public_key,
            'scheme': self.scheme
        }

    def sign_merkle_root(self, merkle_root: str, context: Dict) -> Dict:
        """
        Assina uma raiz Merkle com PQC

        Args:
            merkle_root: Hash da raiz Merkle
            context: Contexto adicional da assinatura

        Returns:
            Dict com assinatura PQC completa
        """
        message = self._prepare_signing_message(merkle_root, context)
        signature = self._simulate_dilithium_sign(message)

        return {
            'merkle_root': merkle_root,
            'signature': signature,
            'public_key': self.keypair['public_key'],
            'scheme': self.scheme,
            'timestamp': self._get_timestamp(),
            'message_hash': hashlib.sha3_256(message.encode()).hexdigest()
        }

    def verify_signature(self, signature_data: Dict) -> bool:
        """
        Verifica assinatura PQC

        Args:
            signature_data: Dados da assinatura

        Returns:
            True se válida, False caso contrário
        """
        # Simulação de verificação
        # Em produção, usar verificação criptográfica real
        required_fields = ['merkle_root', 'signature', 'public_key', 'scheme', 'message_hash']
        return all(field in signature_data for field in required_fields)

    def _prepare_signing_message(self, merkle_root: str, context: Dict) -> str:
        """
        Prepara mensagem para assinatura

        Args:
            merkle_root: Raiz Merkle
            context: Contexto

        Returns:
            Mensagem formatada para assinatura
        """
        return json.dumps({
            'merkle_root': merkle_root,
            'context': context,
            'domain': 'matverse.prime.v1',
            'timestamp': self._get_timestamp()
        }, sort_keys=True)

    def _simulate_dilithium_sign(self, message: str) -> str:
        """
        Simula assinatura Dilithium3

        Args:
            message: Mensagem a assinar

        Returns:
            Assinatura base64
        """
        # Simulação usando SHA3-256 + chave privada
        # Em produção, usar Dilithium real
        simulated_sig = hashlib.sha3_256(
            f"{message}{self.keypair['private_key']}".encode()
        ).hexdigest()
        return base64.b64encode(simulated_sig.encode()).decode()

    def _get_timestamp(self) -> str:
        """Retorna timestamp UTC ISO 8601"""
        return datetime.utcnow().isoformat() + 'Z'


class PQCIntegration:
    """
    Integração PQC com sistema de Evidence Notes
    """

    def __init__(self):
        self.signer = PQCSigner()

    def create_pqc_evidence_note(self, metrics: Dict, context: Dict) -> Dict:
        """
        Cria Evidence Note com assinatura PQC

        Args:
            metrics: Métricas do sistema (omega, psi, theta, etc)
            context: Contexto da operação

        Returns:
            Evidence Note completo com PQC
        """
        # 1. Criar Merkle Tree das métricas
        merkle_tree = self._build_merkle_tree(metrics)

        # 2. Assinar raiz Merkle
        pqc_signature = self.signer.sign_merkle_root(
            merkle_tree['root'],
            context
        )

        # 3. Montar Evidence Note
        evidence_note = {
            'version': '1.0.0',
            'timestamp': self._get_timestamp(),
            'metrics': metrics,
            'merkle_proof': merkle_tree,
            'pqc_signature': pqc_signature,
            'context': context,
            'evidence_id': self._generate_evidence_id(merkle_tree['root'])
        }

        return evidence_note

    def verify_evidence_note(self, evidence_note: Dict) -> bool:
        """
        Verifica integridade de Evidence Note

        Args:
            evidence_note: Evidence Note a verificar

        Returns:
            True se válido, False caso contrário
        """
        # 1. Verificar assinatura PQC
        if not self.signer.verify_signature(evidence_note['pqc_signature']):
            return False

        # 2. Verificar Merkle root
        recomputed_root = self._compute_merkle_root(evidence_note['metrics'])
        if recomputed_root != evidence_note['merkle_proof']['root']:
            return False

        return True

    def _build_merkle_tree(self, metrics: Dict) -> Dict:
        """
        Constrói Merkle Tree das métricas

        Args:
            metrics: Dicionário de métricas

        Returns:
            Dict com raiz e provas Merkle
        """
        # Serializar métricas
        leaves = []
        for key, value in sorted(metrics.items()):
            leaf_data = f"{key}:{value}"
            leaf_hash = hashlib.sha3_256(leaf_data.encode()).hexdigest()
            leaves.append(leaf_hash)

        # Construir árvore (simplificado)
        root = self._compute_merkle_root_from_leaves(leaves)

        return {
            'root': root,
            'leaves': leaves,
            'num_leaves': len(leaves)
        }

    def _compute_merkle_root_from_leaves(self, leaves: List[str]) -> str:
        """
        Computa raiz Merkle de lista de folhas

        Args:
            leaves: Lista de hashes das folhas

        Returns:
            Hash da raiz
        """
        if len(leaves) == 0:
            return hashlib.sha3_256(b'empty').hexdigest()

        if len(leaves) == 1:
            return leaves[0]

        # Combinar pares de hashes
        next_level = []
        for i in range(0, len(leaves), 2):
            if i + 1 < len(leaves):
                combined = leaves[i] + leaves[i + 1]
            else:
                combined = leaves[i] + leaves[i]

            next_level.append(
                hashlib.sha3_256(combined.encode()).hexdigest()
            )

        return self._compute_merkle_root_from_leaves(next_level)

    def _compute_merkle_root(self, metrics: Dict) -> str:
        """
        Computa raiz Merkle das métricas

        Args:
            metrics: Dicionário de métricas

        Returns:
            Hash da raiz
        """
        merkle_tree = self._build_merkle_tree(metrics)
        return merkle_tree['root']

    def _generate_evidence_id(self, merkle_root: str) -> str:
        """
        Gera ID único para Evidence Note

        Args:
            merkle_root: Raiz Merkle

        Returns:
            Evidence ID
        """
        id_hash = hashlib.sha3_256(
            f"{merkle_root}{self._get_timestamp()}".encode()
        ).hexdigest()
        return f"EVD-{id_hash[:16]}"

    def _get_timestamp(self) -> str:
        """Retorna timestamp UTC ISO 8601"""
        return datetime.utcnow().isoformat() + 'Z'


# Teste rápido
if __name__ == "__main__":
    print("🧪 Testando sistema PQC...")

    # Teste 1: Assinatura simples
    pqc = PQCSigner()
    signature = pqc.sign_merkle_root("test_root_hash", {"omega": 0.963})
    print(f"✅ Assinatura PQC gerada: {signature['signature'][:32]}...")

    # Teste 2: Evidence Note completo
    integration = PQCIntegration()
    evidence = integration.create_pqc_evidence_note(
        metrics={'omega': 0.963, 'psi': 0.95, 'theta': 0.0028},
        context={'process': 'kalman_test'}
    )
    print(f"✅ Evidence Note criado: {evidence['evidence_id']}")

    # Teste 3: Verificação
    is_valid = integration.verify_evidence_note(evidence)
    print(f"✅ Verificação: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
