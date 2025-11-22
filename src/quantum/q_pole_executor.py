"""
Q-PoLE (Quantum Proof of Latent Evolution) Executor

Implementa prova quântica de evolução temporal entre versões
de sistemas cognitivos, com validação via fidelidade F ≥ 0.95
"""

import numpy as np
from datetime import datetime
import hashlib
from typing import Dict, Any


class QPoleExecutor:
    """
    Executor de provas quânticas de evolução temporal

    Características:
    - Fidelidade target: F ≥ 0.95
    - Frequência CFC: 0.0071 Hz (padrão)
    - Shots padrão: 8192
    - Backend: Simulação matricial (producão: IBM Quantum)
    """

    def __init__(self, cfc_freq: float = 0.0071):
        self.cfc_freq = cfc_freq
        self.results_history = []

    def create_evolution_circuit(
        self,
        version_t0: Dict[str, Any],
        version_t1: Dict[str, Any]
    ) -> np.ndarray:
        """
        Cria circuito de evolução temporal

        Estrutura:
        1. Estado inicial |000⟩
        2. Encode t0: Ry(θ_t0) em qubit 0
        3. Entanglement: CNOT 0→1, 1→2
        4. Evolução: Rz(ω·Δt) em qubit 0
        5. Decode t1: Ry†(θ_t1) em qubit 0

        Args:
            version_t0: {'omega': float, 'timestamp': datetime}
            version_t1: {'omega': float, 'timestamp': datetime}

        Returns:
            State vector complexo (8 componentes para 3 qubits)
        """
        # Estado inicial |000⟩
        psi = np.zeros(8, dtype=complex)
        psi[0] = 1.0

        # 1. Encode version_t0
        hash_t0 = int(hashlib.sha256(str(version_t0).encode()).hexdigest(), 16)
        theta_t0 = (hash_t0 % 10000) / 10000 * 2 * np.pi
        psi = self._apply_ry(psi, theta_t0, qubit=0)

        # 2. Entanglement
        psi = self._apply_cnot(psi, control=0, target=1)
        psi = self._apply_cnot(psi, control=1, target=2)

        # 3. Evolução temporal
        delta_t = (version_t1['timestamp'] - version_t0['timestamp']).total_seconds()
        evolution_angle = 2 * np.pi * self.cfc_freq * delta_t
        psi = self._apply_rz(psi, evolution_angle, qubit=0)

        # 4. Decode version_t1
        hash_t1 = int(hashlib.sha256(str(version_t1).encode()).hexdigest(), 16)
        theta_t1 = (hash_t1 % 10000) / 10000 * 2 * np.pi
        psi = self._apply_ry(psi, -theta_t1, qubit=0)

        return psi

    def _apply_ry(self, psi: np.ndarray, theta: float, qubit: int) -> np.ndarray:
        """Aplica rotação Ry(θ) no qubit especificado (0=MSB, 2=LSB)"""
        psi_new = np.zeros_like(psi)
        cos_t = np.cos(theta / 2)
        sin_t = np.sin(theta / 2)

        mask = 1 << (2 - qubit)  # Máscara para o qubit

        for i in range(len(psi)):
            if i & mask == 0:  # |0⟩ neste qubit
                psi_new[i] += cos_t * psi[i]
                psi_new[i | mask] += sin_t * psi[i]
            else:  # |1⟩ neste qubit
                psi_new[i] += cos_t * psi[i]
                psi_new[i & ~mask] += -sin_t * psi[i]

        return psi_new

    def _apply_rz(self, psi: np.ndarray, theta: float, qubit: int) -> np.ndarray:
        """Aplica rotação Rz(θ) no qubit especificado"""
        psi_new = psi.copy()
        mask = 1 << (2 - qubit)

        for i in range(len(psi)):
            if i & mask:  # |1⟩
                psi_new[i] *= np.exp(1j * theta / 2)
            else:  # |0⟩
                psi_new[i] *= np.exp(-1j * theta / 2)

        return psi_new

    def _apply_cnot(self, psi: np.ndarray, control: int, target: int) -> np.ndarray:
        """Aplica CNOT entre qubits (0=MSB, 2=LSB)"""
        psi_new = psi.copy()
        control_mask = 1 << (2 - control)
        target_mask = 1 << (2 - target)

        for i in range(len(psi)):
            if i & control_mask:  # Control é |1⟩
                # Swap com target flipped
                j = i ^ target_mask
                psi_new[i] = psi[j]

        return psi_new

    def execute(
        self,
        psi: np.ndarray,
        shots: int = 8192
    ) -> Dict[str, Any]:
        """
        Executa medição do estado quântico

        Args:
            psi: State vector
            shots: Número de medições

        Returns:
            {
                'fidelity': float,  # P(|000⟩)
                'counts': dict,     # Histograma de medições
                'shots': int,
                'entropy': float,
                'top_states': dict
            }
        """
        # Calcula probabilidades
        probs = np.abs(psi)**2
        probs /= probs.sum()

        # Simula medições
        measurements = np.random.choice(len(probs), size=shots, p=probs)

        counts = {}
        for m in measurements:
            bin_str = format(m, '03b')
            counts[bin_str] = counts.get(bin_str, 0) + 1

        # Fidelidade = P(|000⟩)
        fidelity = counts.get('000', 0) / shots

        # Entropia de Shannon
        entropy = -np.sum(probs * np.log2(probs + 1e-10))

        result = {
            'fidelity': fidelity,
            'counts': counts,
            'shots': shots,
            'entropy': entropy,
            'top_states': dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5])
        }

        self.results_history.append(result)
        return result

    def validate_and_anchor(
        self,
        result: Dict[str, Any],
        version_t0: Dict[str, Any],
        version_t1: Dict[str, Any],
        threshold: float = 0.95
    ) -> Dict[str, Any]:
        """
        Valida fidelidade e simula ancoragem blockchain

        Args:
            result: Resultado do execute()
            version_t0, version_t1: Versões comparadas
            threshold: Fidelidade mínima (padrão 0.95)

        Returns:
            {
                'status': 'Q_POLE_APPROVED' | 'INSUFFICIENT_FIDELITY',
                'fidelity': float,
                'merkle_root': str,
                'tx_hash': str,
                'proof_url': str
            }
        """
        fidelity = result['fidelity']

        if fidelity >= threshold:
            # Cria dados da prova
            q_pole_data = {
                'version_t0': version_t0,
                'version_t1': version_t1,
                'fidelity': fidelity,
                'entropy': result['entropy'],
                'timestamp': datetime.utcnow().isoformat(),
                'cfc_freq': self.cfc_freq,
                'top_states': result['top_states']
            }

            # Simula Merkle tree
            merkle_root = hashlib.sha256(str(q_pole_data).encode()).hexdigest()

            # Simula transação Polygon
            tx_hash = f"0x{hashlib.sha256(merkle_root.encode()).hexdigest()}"

            return {
                'status': 'Q_POLE_APPROVED',
                'fidelity': fidelity,
                'merkle_root': merkle_root,
                'tx_hash': tx_hash,
                'proof_url': f'https://matversescan.io/q-pole/{tx_hash}',
                'data': q_pole_data
            }
        else:
            return {
                'status': 'INSUFFICIENT_FIDELITY',
                'fidelity': fidelity,
                'threshold': threshold,
                'retry_recommended': True
            }


def main():
    """Exemplo de uso"""
    # Versões para comparação
    version_t0 = {
        'omega': 0.958,
        'timestamp': datetime(2025, 11, 21, 23, 25, 9)
    }

    version_t1 = {
        'omega': 0.972,
        'timestamp': datetime.utcnow()
    }

    # Inicializa executor
    executor = QPoleExecutor(cfc_freq=0.0071)

    # Cria circuito
    print("🔧 Criando circuito de evolução temporal Q-PoLE...")
    psi = executor.create_evolution_circuit(version_t0, version_t1)
    print(f"   Estado preparado (norma: {np.linalg.norm(psi):.6f})")

    # Executa
    print("\n🚀 Executando simulação (8192 shots)...")
    result = executor.execute(psi, shots=8192)

    print(f"\n✅ Resultados:")
    print(f"   Fidelidade: {result['fidelity']:.4f}")
    print(f"   Entropia: {result['entropy']:.4f}")
    print(f"   Top 5 estados:")
    for state, count in result['top_states'].items():
        prob = count / result['shots']
        print(f"      |{state}⟩: {count:4d} shots ({prob:.3f})")

    # Valida e ancora
    print("\n⚓ Validando e ancorando...")
    proof = executor.validate_and_anchor(result, version_t0, version_t1)

    if proof['status'] == 'Q_POLE_APPROVED':
        print(f"✅ Q-PoLE APROVADO!")
        print(f"   Fidelidade: {proof['fidelity']:.4f}")
        print(f"   Merkle Root: {proof['merkle_root'][:32]}...")
        print(f"   TX Hash: {proof['tx_hash'][:34]}...")
        print(f"   Proof URL: {proof['proof_url']}")
    else:
        print(f"⚠️ Fidelidade insuficiente: {proof['fidelity']:.4f} < {proof['threshold']}")


if __name__ == '__main__':
    main()
