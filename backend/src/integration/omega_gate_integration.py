#!/usr/bin/env python3
"""
Ω-GATE Integration Module
MatVerse Unified Ecosystem - Unified Gateway

Integra Filtro Kalman Adaptativo + PQC Signer + Ω-GATE Governance
para processamento completo de auditoria científica

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

# Adiciona diretório src ao path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from filters.kalman_cfc_adaptive import AdaptiveKalmanCFC
from blockchain.pqc_signer import SPHINCSPlusSigner, PQCEvidenceNote


class OmegaGateProcessor:
    """
    Processador Ω-GATE completo

    Combina:
    - Filtro Kalman Adaptativo (CFC)
    - Assinatura PQC (SPHINCS+)
    - Governança Ω-GATE
    """

    def __init__(self, security_level: int = 128):
        """
        Inicializa o processador Ω-GATE

        Args:
            security_level: Nível de segurança PQC (bits)
        """
        # Componentes
        self.kalman_filter = AdaptiveKalmanCFC()
        self.pqc_signer = SPHINCSPlusSigner(security_level)
        self.evidence_system = PQCEvidenceNote(self.pqc_signer)

        # Pesos do Ω-Score
        self.omega_weights = {
            'psi': 0.4,      # Qualidade semântica
            'theta': 0.25,    # Performance
            'cvar': 0.15,     # Risco
            'pole': 0.08,     # Evolução
            'cog': 0.05,      # Governança
            'trust': 0.07     # Confiança
        }

    def calculate_omega_score(self,
                             psi: float,
                             theta_ms: float,
                             cvar: float = 0.01,
                             pole: float = 0.5,
                             cog: float = 0.8,
                             trust: float = 0.9) -> float:
        """
        Calcula Ω-Score integrado

        Ω = w_ψ·Ψ + w_θ·Θ⁻¹ + w_CVaR·(1-CVaR) + w_PoLE·PoLE + w_COG·COG + w_T·T

        Args:
            psi: Qualidade semântica (0-1)
            theta_ms: Latência em ms
            cvar: Risco condicional (0-1)
            pole: Prova de Evolução Latente (0-1)
            cog: Coeficiente de Governança (0-1)
            trust: Trust Score dinâmico (0-1)

        Returns:
            Ω-Score normalizado (0-1)
        """
        # Normaliza Θ (latência)
        # Assume 20ms = excelente (1.0), 500ms = ruim (0.0)
        theta_norm = max(0, min(1, 1 - (theta_ms - 20) / 480))

        # Calcula Ω
        omega = (
            self.omega_weights['psi'] * psi +
            self.omega_weights['theta'] * theta_norm +
            self.omega_weights['cvar'] * (1 - cvar) +
            self.omega_weights['pole'] * pole +
            self.omega_weights['cog'] * cog +
            self.omega_weights['trust'] * trust
        )

        return float(omega)

    def process_comprehensive_audit(self,
                                   psi_series: List[float],
                                   gamma_series: List[float],
                                   context: Optional[Dict] = None) -> Dict:
        """
        Processa auditoria completa com Kalman + PQC + Ω-GATE

        Args:
            psi_series: Série temporal de Ψ
            gamma_series: Série temporal de Γ
            context: Contexto adicional da auditoria

        Returns:
            Resultado completo da auditoria
        """
        start_time = time.time()

        if context is None:
            context = {}

        # 1. FILTRO KALMAN - Otimização CFC
        print("🧮 Executando Filtro Kalman Adaptativo...")
        kalman_results = self.kalman_filter.optimize_cfc(
            psi_series,
            gamma_series,
            max_iterations=50,
            correlation_threshold=-0.95
        )

        # 2. CÁLCULO Ω-SCORE
        print("🎯 Calculando Ω-Score...")

        # Usa fidelidade do Kalman como Ψ
        psi_quality = kalman_results['fidelity']

        # Latência simulada baseada no tempo de processamento
        theta_ms = kalman_results['processing_time_ms']

        # CVaR baseado na coerência (baixa coerência = alto risco)
        cvar_risk = 1.0 - kalman_results['coherence']

        omega_score = self.calculate_omega_score(
            psi=psi_quality,
            theta_ms=theta_ms,
            cvar=cvar_risk,
            pole=0.65,  # Placeholder
            cog=0.85,   # Placeholder
            trust=0.92  # Placeholder
        )

        # 3. ASSINATURA PQC - Evidence Note
        print("🛡️ Gerando Evidence Note com assinatura PQC...")

        evidence_content = {
            'audit_type': 'comprehensive_kalman_cfc',
            'kalman_results': {
                'correlation_initial': kalman_results['correlation_initial'],
                'correlation_final': kalman_results['correlation_final'],
                'correlation_gain': kalman_results['correlation_gain'],
                'fidelity': kalman_results['fidelity'],
                'coherence': kalman_results['coherence'],
                'cfc_score': kalman_results['cfc_score'],
                'iterations': kalman_results['iterations'],
                'converged': kalman_results['converged']
            },
            'omega_gate': {
                'omega_score': omega_score,
                'psi_quality': psi_quality,
                'theta_latency_ms': theta_ms,
                'cvar_risk': cvar_risk,
                'weights': self.omega_weights
            },
            'context': context,
            'processing_time_ms': kalman_results['processing_time_ms']
        }

        evidence_note = self.evidence_system.create_evidence(
            evidence_content,
            evidence_type="COMPREHENSIVE_AUDIT"
        )

        # 4. VALIDAÇÃO PQC
        print("✅ Validando Evidence Note...")
        is_valid, validation_msg = self.evidence_system.verify_evidence(evidence_note)

        # Tempo total de processamento
        total_time_ms = (time.time() - start_time) * 1000

        # 5. RESULTADO UNIFICADO
        result = {
            'success': True,
            'audit_id': evidence_note['id'],
            'timestamp': evidence_note['timestamp'],

            # Resultados Kalman
            'kalman': {
                'correlation_initial': kalman_results['correlation_initial'],
                'correlation_final': kalman_results['correlation_final'],
                'correlation_gain': kalman_results['correlation_gain'],
                'fidelity_new': kalman_results['fidelity'],
                'coherence': kalman_results['coherence'],
                'cfc_score': kalman_results['cfc_score'],
                'iterations': kalman_results['iterations'],
                'converged': kalman_results['converged'],
                'processing_time_ms': kalman_results['processing_time_ms']
            },

            # Ω-GATE Governance
            'omega_gate': {
                'omega_score': omega_score,
                'psi_quality': psi_quality,
                'theta_latency_ms': theta_ms,
                'cvar_risk': cvar_risk,
                'approved': omega_score >= 0.7,
                'tier': self._get_omega_tier(omega_score)
            },

            # Evidence Note + PQC
            'evidence_note': {
                'id': evidence_note['id'],
                'pqc_signature': evidence_note['pqc_signature']['signature'],
                'public_key': evidence_note['pqc_signature']['public_key'],
                'algorithm': evidence_note['pqc_signature']['algorithm'],
                'verified': is_valid,
                'verification_msg': validation_msg,
                'verification_url': evidence_note['verification_url']
            },

            # Métricas de Performance
            'performance': {
                'total_time_ms': total_time_ms,
                'kalman_time_ms': kalman_results['processing_time_ms'],
                'overhead_ms': total_time_ms - kalman_results['processing_time_ms']
            },

            # Validação Final
            'validation': {
                'kalman_converged': kalman_results['converged'],
                'omega_approved': omega_score >= 0.7,
                'pqc_verified': is_valid,
                'checks_passed': sum([
                    kalman_results['converged'],
                    omega_score >= 0.7,
                    is_valid
                ]),
                'total_checks': 3
            }
        }

        return result

    def _get_omega_tier(self, omega_score: float) -> str:
        """
        Determina tier baseado no Ω-Score

        Args:
            omega_score: Score de 0 a 1

        Returns:
            Nome do tier
        """
        if omega_score >= 0.95:
            return "VERDADE² (Elite)"
        elif omega_score >= 0.85:
            return "VERDADE¹ (Premium)"
        elif omega_score >= 0.70:
            return "APROVADO (Standard)"
        else:
            return "REVISÃO NECESSÁRIA"


def demo_integration():
    """Demonstração da integração completa"""
    print("🌟 Ω-GATE INTEGRATION - COMPREHENSIVE AUDIT DEMO")
    print("=" * 80)

    # Cria processador
    processor = OmegaGateProcessor(security_level=128)

    # Dados de teste: Ψ e Γ anticorrelacionados
    np.random.seed(42)
    n_samples = 15

    psi_series = np.linspace(-0.8, 1.2, n_samples) + np.random.normal(0, 0.1, n_samples)
    gamma_series = -psi_series + np.random.normal(0, 0.15, n_samples)

    # Contexto da auditoria
    context = {
        'type': 'test_integration_demo',
        'frequency_hz': 50,
        'quantum_states': 46080,
        'operation_mode': 'full_audit'
    }

    # Executa auditoria completa
    result = processor.process_comprehensive_audit(
        psi_series.tolist(),
        gamma_series.tolist(),
        context=context
    )

    # Exibe resultados
    print("\n📊 RESULTADOS DA AUDITORIA COMPLETA:")
    print(f"✅ Sucesso: {result['success']}")
    print(f"🆔 Audit ID: {result['audit_id']}")
    print()

    print("🧮 KALMAN CFC:")
    k = result['kalman']
    print(f"  📈 Correlação inicial: {k['correlation_initial']:.3f}")
    print(f"  🎯 Correlação final: {k['correlation_final']:.3f}")
    print(f"  🚀 Ganho: {k['correlation_gain']:.3f}")
    print(f"  ⚛️ Fidelidade: {k['fidelity_new']:.6f}")
    print(f"  🌀 Coerência: {k['coherence']:.6f}")
    print(f"  🏆 CFC Score: {k['cfc_score']:.6f}")
    print(f"  🔄 Iterações: {k['iterations']}")
    print(f"  ✔️ Convergiu: {k['converged']}")
    print()

    print("🎯 Ω-GATE GOVERNANCE:")
    o = result['omega_gate']
    print(f"  🌟 Ω-Score: {o['omega_score']:.3f}")
    print(f"  📊 Ψ Quality: {o['psi_quality']:.3f}")
    print(f"  ⏱️ Θ Latency: {o['theta_latency_ms']:.1f}ms")
    print(f"  ⚠️ CVaR Risk: {o['cvar_risk']:.3f}")
    print(f"  ✅ Aprovado: {o['approved']}")
    print(f"  🏆 Tier: {o['tier']}")
    print()

    print("🛡️ EVIDENCE NOTE + PQC:")
    e = result['evidence_note']
    print(f"  🆔 Evidence ID: {e['id']}")
    print(f"  🔐 PQC Signature: {e['pqc_signature'][:32]}...")
    print(f"  🔑 Public Key: {e['public_key'][:32]}...")
    print(f"  🛡️ Algorithm: {e['algorithm']}")
    print(f"  ✅ Verificado: {e['verified']}")
    print(f"  📋 {e['verification_msg']}")
    print()

    print("⚡ PERFORMANCE:")
    p = result['performance']
    print(f"  ⏱️ Tempo total: {p['total_time_ms']:.1f}ms")
    print(f"  🧮 Kalman: {p['kalman_time_ms']:.1f}ms")
    print(f"  📦 Overhead: {p['overhead_ms']:.1f}ms")
    print()

    print("✅ VALIDAÇÃO FINAL:")
    v = result['validation']
    print(f"  🔍 Checks passados: {v['checks_passed']}/{v['total_checks']}")
    print(f"  ✔️ Kalman convergiu: {v['kalman_converged']}")
    print(f"  ✔️ Ω aprovado: {v['omega_approved']}")
    print(f"  ✔️ PQC verificado: {v['pqc_verified']}")

    print("\n" + "=" * 80)
    print("🎉 AUDITORIA COMPLETA FINALIZADA COM SUCESSO!")


if __name__ == "__main__":
    demo_integration()
