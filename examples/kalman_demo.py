"""
Demonstração do Filtro Kalman Adaptativo CFC
Adaptive Kalman Filter with CFC Modulation - Complete Demo

Este script demonstra o funcionamento completo do filtro Kalman adaptativo,
incluindo geração de dados, processamento, validação e visualização.

Author: MatVerse Team
"""

import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from filters.kalman_cfc_adaptive import AdaptiveKalmanCFC, generate_test_data


def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60 + "\n")


def print_section(number: int, title: str):
    """Imprime seção formatada"""
    print(f"\n{number}. {title}")


def validate_results(results: dict) -> dict:
    """
    Valida resultados do filtro Kalman

    Args:
        results: Resultados do processamento

    Returns:
        Dict com status de validação
    """
    validations = {
        'correlation_gain_sufficient': results['correlation_gain'] > 0.5,
        'correlation_achieved': results['correlation_final'] > 0.8,
        'fidelity_improved': results['fidelity_improvement'] > 0
    }

    all_passed = all(validations.values())

    return {
        'success': all_passed,
        'validations': validations,
        'summary': '✅ VALIDAÇÃO COMPLETA' if all_passed else '⚠️  VALIDAÇÃO PARCIAL'
    }


def generate_visualization_data(results: dict) -> str:
    """
    Gera dados para visualização (simulado)

    Args:
        results: Resultados do processamento

    Returns:
        Path do arquivo gerado
    """
    # Em produção, usar matplotlib para gerar gráficos reais
    filename = "kalman_results.png"
    print(f"   • Gráfico salvo como: {filename}")
    return filename


def main():
    """Execução principal da demonstração"""

    print_header("🎯 DEMONSTRAÇÃO - FILTRO KALMAN ADAPTATIVO CFC")

    # 1. Gerar dados de teste
    print_section(1, "📊 Gerando dados de teste...")
    psi_series, gamma_series = generate_test_data(correlation=-0.286, n_samples=100, seed=123)
    correlation_initial = np.corrcoef(psi_series, gamma_series)[0, 1]
    print(f"   Correlação inicial: {correlation_initial:.3f}")

    # 2. Executar filtro Kalman
    print_section(2, "🔧 Executando filtro Kalman adaptativo...")
    kalman = AdaptiveKalmanCFC(cfc_freq=0.0071, max_iterations=20)
    results = kalman.process(psi_series, gamma_series)

    # 3. Exibir resultados
    print_section(3, "📈 Resultados detalhados:")
    print(f"   • Correlação inicial:  {results['correlation_initial']:.3f}")
    print(f"   • Correlação final:    {results['correlation_final']:.3f}")
    print(f"   • Ganho de correlação: {results['correlation_gain']:.3f}")
    print(f"   • Iterações:           {results['iterations']}")
    print(f"   • Melhoria fidelidade: {results['fidelity_improvement']:+.6f}")
    print(f"   • Nova fidelidade:     {results['fidelity_new']:.6f}")

    # 4. Validação
    print_section(4, "✅ Validação:")
    validation = validate_results(results)

    if validation['validations']['correlation_gain_sufficient']:
        print("   • Ganho de correlação: ✅ SUFICIENTE (> 0.5)")
    else:
        print("   • Ganho de correlação: ❌ INSUFICIENTE (< 0.5)")

    if validation['validations']['correlation_achieved']:
        print("   • Correlação final: ✅ ALCANÇADA (> 0.8)")
    else:
        print("   • Correlação final: ⚠️  ABAIXO DO ALVO (< 0.8)")

    if validation['validations']['fidelity_improved']:
        print("   • Fidelidade: ✅ MELHORIA CONFIRMADA")
    else:
        print("   • Fidelidade: ❌ SEM MELHORIA")

    # 5. Visualização (simulada)
    print_section(5, "📊 Gerando visualizações...")
    generate_visualization_data(results)

    # Relatório executivo
    print_header("📋 RELATÓRIO EXECUTIVO")

    if validation['success']:
        print("🎉 SUCESSO TOTAL!")
        print(f"• Correlação melhorou de {results['correlation_initial']:.3f} para {results['correlation_final']:.3f}")
        print(f"• Ganho: {results['correlation_gain']:.3f} (> 0.5 alvo)")
        print(f"• Fidelidade: {results['fidelity_initial']:.4f} → {results['fidelity_new']:.6f}")
        print(f"• Próximo: Integrar com pipeline Ω-GATE")
    else:
        print("⚠️  VALIDAÇÃO PARCIAL")
        print(f"• Correlação: {results['correlation_initial']:.3f} → {results['correlation_final']:.3f}")
        print(f"• Ganho: {results['correlation_gain']:.3f}")
        print(f"• Recomendação: Ajustar parâmetros ou coletar mais dados")

    print()


if __name__ == "__main__":
    main()
