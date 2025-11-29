# SymbiOS – Pipeline Antifrágil (Ω/Ψ/CVaR)

Este guia descreve como o SymbiOS passa a reagir a falhas de forma antifrágil: cada degradação de Ω dispara rollback, registra um evento de aprendizado e recalibra automaticamente os pesos de Ψ e a penalidade de CVaR.

## Visão Geral
- **Observabilidade**: `omega_exporter.py` lê a evidência do Ω-GATE/PoSE e publica métricas Prometheus (`symbios_omega_score`, `symbios_psi_score`, `symbios_cvar_score`).
- **CI/CD**: `.github/workflows/antifragile.yml` interrompe o pipeline se Ω < limiar (padrão 0.85) e aciona rollback automático.
- **Aprendizado**: `rollback_logger.py` registra quedas e `adaptive_tune.py` recalibra pesos/limiares para reduzir recorrência.
- **Operação local**: `Dockerfile.exporter` sobe Prometheus + exporter numa única imagem; o dashboard Grafana incluso lê as mesmas métricas.
- **Teste de estresse**: `scripts/stress_simulator.py` envia cargas que degradam Ψ para validar o comportamento antifrágil fim-a-fim.

## Métricas
- **Ω (Omega)**: média móvel de Ψ ponderada por penalidade de CVaR (risco de cauda).
- **Ψ (Psi)**: qualidade do julgamento do Ω-GATE em evidências recentes.
- **CVaR**: média das piores perdas `(1-Ψ)` no nível de confiança configurado (`cvar_alpha`, padrão 95%).

## Exporter
```bash
# Coleta única (útil em CI)
python omega_exporter.py --once

# Servidor Prometheus (porta 8000 por padrão)
python omega_exporter.py --port 8000 --interval 10 --window 200
```

Ajustes em `antifragile_config.json`:
- `omega_threshold`: limiar de Ω para bloquear/rollback.
- `psi_weight`: peso de Ψ no cálculo de Ω.
- `cvar_penalty`: penalidade aplicada ao CVaR.
- `cvar_alpha`: nível de confiança do CVaR.
- `window_size`: eventos recentes usados no cálculo.

## Rollback e Aprendizado
1. `log_rollback` escreve `antifragile_log.jsonl` com `omega_old`, `omega_new` e `antifragile_gain`.
2. `record_failure_threshold_breach` ajusta `omega_threshold` para endurecer o gate.
3. `tune_after_rollback` aplica heurísticas pós-rollback (peso extra para Ψ, penalidade de CVaR +5%).

## Pipeline CI/CD antifrágil
Fluxo no `.github/workflows/antifragile.yml`:
1. Instala dependências e roda `pytest` (pode ser substituído por suites internas).
2. Sobe o exporter em background e coleta métricas atuais.
3. Falha o job se `symbios_omega_score < omega_threshold`.
4. Em falha, loga rollback antifrágil (mantendo histórico para tuning).

## Observabilidade local
1. **Build**: `docker build -f Dockerfile.exporter -t symbios-antifragile .`
2. **Run**: `docker run -p 8000:8000 -p 9090:9090 symbios-antifragile`
   - Exporter: `http://localhost:8000/metrics`
   - Prometheus: `http://localhost:9090`
3. **Grafana**: importe `monitoring/grafana_dashboard.json` e aponte para o Prometheus acima.

## Simulador de estresse
Use o script para gerar degradação controlada de Ψ/Ω.
```bash
python scripts/stress_simulator.py --server http://localhost:8000 --intensity 0.9
```
O simulador envia payloads malformados para o Ω-GATE, reduz Ψ e permite validar a reversão automática.

## Troubleshooting
- **Sem evidências**: o exporter usa `omega_threshold` como fallback até que `symbios/evidence.json` seja populado.
- **CVaR alto**: aumente `cvar_penalty` ou `cvar_alpha` em `antifragile_config.json` e rode `adaptive_tune.py` após novos rollbacks.
- **Threshold**: edite `omega_threshold` ou deixe o `log_and_tune` ajustar automaticamente após incidentes.
