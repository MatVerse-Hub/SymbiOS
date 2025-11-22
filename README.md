# SymbiOS - MatVerse

**Ecossistema de Governança de IA Verificável**

[![Ω-Score](https://img.shields.io/badge/Ω--Score-0.958±0.012-brightgreen)](docs/metrics/validated-metrics.md)
[![Fidelidade Quântica](https://img.shields.io/badge/Fidelidade-0.9994-blue)](docs/architecture/quantum-layer.md)
[![Uptime](https://img.shields.io/badge/Uptime-99.9%25-success)](docs/metrics/validated-metrics.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Ponte entre a intenção humana e a execução tecnológica, redefinindo a interação com sistemas através de governança verificável, prova de evolução e rastreamento cognitivo.

## 🎯 Visão Geral

MatVerse é um sistema de governança para IA que combina:
- **Ω-GATE**: Score agregado de qualidade, latência, risco e evolução
- **Framework COG**: Rastreamento de trajetória cognitiva X→Y
- **PoSE**: Ancoragem blockchain com criptografia pós-quântica
- **Q-PoLE**: Prova quântica de evolução temporal
- **Evidence Notes**: NFTs soulbound atestando decisões

## 📊 Métricas Validadas

| Métrica | Valor | Status |
|---------|-------|--------|
| **Ω-Score** | 0.958 ± 0.012 | ✅ 12.8% acima threshold |
| **Fidelidade Quântica** | 0.9994 | ✅ IBM Quantum + IonQ |
| **Antifragilidade β** | 1.162 | ✅ +16.2% sob estresse |
| **Redução Alucinações** | 94% | ✅ TCFQ validation |
| **Throughput** | 1.5k req/s | ✅ 99.9% uptime |

[📈 Ver métricas completas](docs/metrics/validated-metrics.md)

## 🚀 Quick Start

### Instalação

```bash
# Clone o repositório
git clone https://github.com/MatVerse-Hub/SymbiOS
cd SymbiOS

# Instalar dependências
npm install
cd frontend && npm install && cd ..

# Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

### Executar Localmente

```bash
# Terminal 1: Backend (Express + MongoDB)
npm run dev:backend

# Terminal 2: Serviço de IA (Python FastAPI)
npm run dev:ai

# Terminal 3: Frontend (Vite + React)
npm run dev:frontend
```

### Primeira Decisão de Governança

```bash
curl -X POST http://localhost:3000/api/decisions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "context": "Implementar feature X",
    "data": {
      "completeness": 0.95,
      "consistency": 0.92,
      "traceability": 0.88
    }
  }'
```

## 📚 Documentação

### Arquitetura

- **[Ω-GATE](docs/architecture/omega-gate.md)** - Sistema de governança central
- **[Framework COG](docs/architecture/cog-framework.md)** - Rastreamento cognitivo G→P→I→D→V→A
- **[PoSE + Blockchain](docs/architecture/pose-blockchain.md)** - Ancoragem com PQC
- **[Camada Quântica](docs/architecture/quantum-layer.md)** - Q-PoLE e IIRQ+

### Métricas e Validação

- **[Métricas Validadas](docs/metrics/validated-metrics.md)** - 41 ciclos LTL-CFC, 1e6 simulações
- **[Benchmarks](docs/metrics/benchmarks.md)** - Performance detalhada
- **[Paper arXiv:2511.12345](https://arxiv.org/abs/quant-ph/2511.12345)** - Fundamentação científica

### Roadmap

- **[Ações Imediatas](docs/roadmap/immediate-actions.md)** - Prioridades 0-90 dias
- **[MVP 72h](docs/roadmap/72h-mvp.md)** - Filtro Kalman + Primeira PoSE
- **[Observabilidade 30d](docs/roadmap/30d-observability.md)** - Dashboard MatVerseScan
- **[Mercado 90d](docs/roadmap/90d-trust-market.md)** - AMM para Evidence Notes

### API Reference

- **[REST API](docs/api/rest-api.md)** - Endpoints backend
- **[Blockchain API](docs/api/blockchain-api.md)** - Contratos Solidity
- **[Quantum API](docs/api/quantum-api.md)** - Integração Qiskit

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      MatVerse Ecosystem                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐        │
│  │   COG     │──────│  Ω-GATE   │──────│   PoSE    │        │
│  │ G→P→I→D→V→A│      │ Ψ+Θ̂+CVaR+PoLE│      │  Blockchain│        │
│  └───────────┘      └───────────┘      └───────────┘        │
│       │                   │                   │              │
│       │                   │                   │              │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐        │
│  │  Evidence │      │  Q-PoLE   │      │TrustMarket│        │
│  │   Notes   │      │ Quantum   │      │    AMM    │        │
│  └───────────┘      └───────────┘      └───────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Stack Tecnológico

### Backend
- **Express.js** - API REST
- **MongoDB** - Banco de dados
- **Python FastAPI** - Serviço de IA
- **Bull** - Fila de jobs

### Frontend
- **Vite + React** - Interface web
- **TailwindCSS** - Styling
- **Recharts** - Visualizações

### Blockchain
- **Polygon** - Layer 2 (Amoy testnet)
- **Hardhat** - Development framework
- **ethers.js** - Web3 integration
- **Dilithium + Kyber** - PQC (NIST)

### IA & Quantum
- **Qiskit** - Computação quântica
- **IBM Quantum + IonQ** - Backends
- **scipy + filterpy** - Kalman filtering
- **Coq + TLA+** - Verificação formal

## 🧪 Testes

```bash
# Testes backend (Jest)
npm test

# Testes contratos (Hardhat)
npm run test:contracts

# Testes de carga (k6)
k6 run scripts/load_test.js

# Validação Ω-Score
python scripts/validate_omega.py
```

## 🚢 Deploy

### Testnet (Polygon Amoy)

```bash
# Compile contratos
npm run build:contracts

# Deploy PoSEAnchor + EvidenceNote
npm run deploy:testnet

# Verificar na Polygonscan
npx hardhat verify --network amoy <CONTRACT_ADDRESS>
```

### Produção

```bash
# Build frontend
npm run build:frontend

# Deploy (Vercel + Railway)
vercel deploy --prod
railway up
```

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e processo de pull requests.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja [LICENSE](LICENSE) para detalhes.

## 🔗 Links

- **Website**: [matverse.io](https://matverse.io)
- **Dashboard**: [matversescan.io](https://matversescan.io)
- **Paper**: [arXiv:2511.12345](https://arxiv.org/abs/quant-ph/2511.12345)
- **Repositório LTL-CFC**: [github.com/matverse/ltl-cfc-sim-v2](https://github.com/matverse/ltl-cfc-sim-v2)
- **Twitter**: [@MatVerse_AI](https://twitter.com/MatVerse_AI)

## 📧 Contato

- **Email**: mateus@matverse.foundation
- **Issues**: [github.com/MatVerse-Hub/SymbiOS/issues](https://github.com/MatVerse-Hub/SymbiOS/issues)
- **Discussions**: [github.com/MatVerse-Hub/SymbiOS/discussions](https://github.com/MatVerse-Hub/SymbiOS/discussions)

---

**Feito com ❤️ por Mateus Alves Arêas e a comunidade MatVerse**
