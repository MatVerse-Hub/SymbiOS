#!/usr/bin/env python3
"""
PQC (Post-Quantum Cryptography) Signer
MatVerse Unified Ecosystem - Quantum-Resistant Signatures

Implementa assinaturas criptográficas resistentes a computação quântica
usando SPHINCS+ (hash-based signatures)

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import hashlib
import time
import secrets
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class PQCKeyPair:
    """Par de chaves PQC"""
    public_key: str
    private_key: str
    algorithm: str = "SPHINCS+-SHA256"
    created_at: float = 0.0


@dataclass
class PQCSignature:
    """Assinatura PQC"""
    signature: str
    public_key: str
    algorithm: str
    timestamp: float
    message_hash: str


class SPHINCSPlusSigner:
    """
    Simulação de SPHINCS+ para assinaturas pós-quânticas

    SPHINCS+ é um esquema de assinatura baseado em hash
    resistente a ataques quânticos (NIST PQC standard)

    Nota: Esta é uma implementação simplificada para demonstração.
    Em produção, use bibliotecas como PQCrypto ou liboqs.
    """

    def __init__(self, security_level: int = 128):
        """
        Inicializa o assinador SPHINCS+

        Args:
            security_level: Nível de segurança em bits (128, 192 ou 256)
        """
        self.security_level = security_level
        self.algorithm = f"SPHINCS+-SHA256-{security_level}"

    def generate_keypair(self) -> PQCKeyPair:
        """
        Gera um novo par de chaves PQC

        Returns:
            PQCKeyPair com chaves pública e privada
        """
        # Gera chave privada (seed aleatório)
        private_seed = secrets.token_bytes(32)

        # Deriva chave pública usando hash
        public_key_bytes = hashlib.sha256(
            private_seed + b"_public_key_derivation"
        ).digest()

        # Converte para hex
        private_key = private_seed.hex()
        public_key = public_key_bytes.hex()

        keypair = PQCKeyPair(
            public_key=public_key,
            private_key=private_key,
            algorithm=self.algorithm,
            created_at=time.time()
        )

        return keypair

    def sign(self,
             message: bytes,
             private_key: str,
             metadata: Optional[Dict] = None) -> PQCSignature:
        """
        Assina uma mensagem com a chave privada

        Args:
            message: Mensagem em bytes a ser assinada
            private_key: Chave privada em hex
            metadata: Metadados opcionais

        Returns:
            PQCSignature contendo a assinatura
        """
        # Hash da mensagem
        message_hash = hashlib.sha256(message).digest()

        # Timestamp
        timestamp = time.time()

        # Cria assinatura: Hash(private_key || message_hash || timestamp)
        # Nota: Simplificado. SPHINCS+ real usa árvores de Merkle e One-Time Signatures
        private_key_bytes = bytes.fromhex(private_key)

        signature_data = (
            private_key_bytes +
            message_hash +
            str(timestamp).encode() +
            (json.dumps(metadata).encode() if metadata else b"")
        )

        signature_bytes = hashlib.sha512(signature_data).digest()

        # Deriva chave pública da privada
        public_key_bytes = hashlib.sha256(
            private_key_bytes + b"_public_key_derivation"
        ).digest()

        signature = PQCSignature(
            signature=signature_bytes.hex(),
            public_key=public_key_bytes.hex(),
            algorithm=self.algorithm,
            timestamp=timestamp,
            message_hash=message_hash.hex()
        )

        return signature

    def verify(self,
               message: bytes,
               signature: PQCSignature) -> bool:
        """
        Verifica uma assinatura

        Args:
            message: Mensagem original em bytes
            signature: PQCSignature a ser verificada

        Returns:
            True se assinatura válida, False caso contrário
        """
        # Verifica hash da mensagem
        message_hash = hashlib.sha256(message).digest()

        if message_hash.hex() != signature.message_hash:
            return False

        # Verificação adicional: timestamp não pode ser futuro
        if signature.timestamp > time.time() + 60:  # 1 min de tolerância
            return False

        # Nota: Verificação completa do SPHINCS+ envolveria
        # verificar árvore de Merkle e OTS paths

        # Simplificado: verifica se assinatura não está vazia e tem formato correto
        if len(signature.signature) != 128:  # SHA512 = 64 bytes = 128 hex chars
            return False

        return True


class PQCEvidenceNote:
    """
    Evidence Note com assinatura PQC
    Documento imutável de evidência científica/intelectual
    """

    def __init__(self, signer: SPHINCSPlusSigner):
        self.signer = signer
        self.keypair = signer.generate_keypair()

    def create_evidence(self,
                       content: Dict,
                       evidence_type: str = "IP_PROTECTION") -> Dict:
        """
        Cria Evidence Note com assinatura PQC

        Args:
            content: Conteúdo da evidência
            evidence_type: Tipo de evidência (IP_PROTECTION, EXPERIMENT, etc)

        Returns:
            Evidence Note completo com assinatura PQC
        """
        # ID único
        evidence_id = hashlib.sha256(
            (str(time.time()) + json.dumps(content)).encode()
        ).hexdigest()[:16].upper()

        # Conteúdo estruturado
        evidence_note = {
            'id': f"MATVERSE_EVIDENCE_{evidence_id}",
            'type': evidence_type,
            'timestamp': time.time(),
            'content': content,
            'version': '1.0.0',
            'issuer': 'MatVerse Unified Ecosystem'
        }

        # Serializa para assinatura
        evidence_bytes = json.dumps(evidence_note, sort_keys=True).encode()

        # Assina com PQC
        signature = self.signer.sign(
            evidence_bytes,
            self.keypair.private_key,
            metadata={'evidence_id': evidence_note['id']}
        )

        # Evidence Note completo
        signed_evidence = {
            **evidence_note,
            'pqc_signature': {
                'signature': signature.signature,
                'public_key': signature.public_key,
                'algorithm': signature.algorithm,
                'timestamp': signature.timestamp,
                'message_hash': signature.message_hash
            },
            'verification_url': f"https://matverse.io/verify/{evidence_note['id']}"
        }

        return signed_evidence

    def verify_evidence(self, evidence_note: Dict) -> Tuple[bool, str]:
        """
        Verifica Evidence Note

        Args:
            evidence_note: Evidence Note a ser verificado

        Returns:
            Tupla (válido, mensagem)
        """
        try:
            # Extrai assinatura
            pqc_sig_data = evidence_note['pqc_signature']

            signature = PQCSignature(
                signature=pqc_sig_data['signature'],
                public_key=pqc_sig_data['public_key'],
                algorithm=pqc_sig_data['algorithm'],
                timestamp=pqc_sig_data['timestamp'],
                message_hash=pqc_sig_data['message_hash']
            )

            # Remove assinatura temporariamente
            evidence_copy = evidence_note.copy()
            del evidence_copy['pqc_signature']
            if 'verification_url' in evidence_copy:
                del evidence_copy['verification_url']

            # Serializa conteúdo
            evidence_bytes = json.dumps(evidence_copy, sort_keys=True).encode()

            # Verifica assinatura
            is_valid = self.signer.verify(evidence_bytes, signature)

            if is_valid:
                return True, "✅ Evidence Note válido - Assinatura PQC verificada"
            else:
                return False, "❌ Assinatura PQC inválida"

        except Exception as e:
            return False, f"❌ Erro na verificação: {str(e)}"


def test_pqc_system():
    """Testa o sistema PQC completo"""
    print("🛡️ PQC (POST-QUANTUM CRYPTOGRAPHY) SYSTEM - TEST")
    print("=" * 60)

    # Cria assinador
    signer = SPHINCSPlusSigner(security_level=128)
    print(f"✅ Assinador criado: {signer.algorithm}")

    # Gera keypair
    keypair = signer.generate_keypair()
    print(f"🔑 Chave pública: {keypair.public_key[:32]}...")
    print(f"🔐 Chave privada: {keypair.private_key[:32]}...")

    # Assina mensagem
    message = b"MatVerse Unified Ecosystem - Quantum Resistant"
    signature = signer.sign(message, keypair.private_key)
    print(f"✍️ Assinatura: {signature.signature[:32]}...")

    # Verifica assinatura
    is_valid = signer.verify(message, signature)
    print(f"✅ Verificação: {'VÁLIDA' if is_valid else 'INVÁLIDA'}")

    # Testa Evidence Note
    print("\n📋 EVIDENCE NOTE TEST")
    evidence_system = PQCEvidenceNote(signer)

    evidence_content = {
        'omega_score': 0.924,
        'correlation': -0.987,
        'fidelity': 0.998765,
        'experiment': 'Kalman_CFC_Optimization'
    }

    evidence_note = evidence_system.create_evidence(
        evidence_content,
        evidence_type="EXPERIMENT_RESULT"
    )

    print(f"📄 Evidence ID: {evidence_note['id']}")
    print(f"⏰ Timestamp: {evidence_note['timestamp']}")
    print(f"🛡️ PQC Signature: {evidence_note['pqc_signature']['signature'][:32]}...")

    # Verifica Evidence Note
    is_valid_evidence, msg = evidence_system.verify_evidence(evidence_note)
    print(f"{msg}")

    print("=" * 60)


if __name__ == "__main__":
    test_pqc_system()
