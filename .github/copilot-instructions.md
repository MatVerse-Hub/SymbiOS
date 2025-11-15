<!-- Orientações geradas automaticamente para agentes IA. Mantenha concisas e específicas ao repositório. -->
# SymbiOS — Instruções para agentes Copilot/AI

Este arquivo reúne o conhecimento essencial específico do repositório para que um agente IA seja produtivo rapidamente.

**Visão geral**
- **Backend:** `backend/server.js` — Express + Mongoose (MongoDB). Rotas em `backend/routes/` e modelos em `backend/models/`.
- **Serviço de IA:** `backend/ai/core.py` — serviço Python (FastAPI) responsável pela calibração/retorno de `omega_score`. Iniciado com `npm run dev:ai`. O backend chama via `AI_SERVICE_URL` (veja `backend/routes/decisions.js`).
- **Frontend:** `frontend/` — Vite + React. Entrada: `frontend/src/main.jsx`. Páginas em `frontend/src/pages/`.
- **Contratos:** `contracts/` — projeto Hardhat com contratos Solidity e `scripts/deploy.js`.

**Pontos de integração críticos**
- Fluxo de decisões: `backend/routes/decisions.js` faz `axios.post(`${AI_SERVICE_URL}/calibrate`)` e salva um documento `Decision` (`backend/models/Decision.js`).
- Autenticação: tokens JWT criados com `jwt-simple` em `backend/routes/auth.js` e validados em `backend/middleware/auth.js`. Cabeçalho esperado: `Authorization: Bearer <token>`.
- Ancoragem em blockchain: existe um `TODO: Anchor to blockchain` em `backend/routes/decisions.js`. Compilar contratos: `npm run build:contracts`.

**Comandos principais (do `package.json`)**
- `npm run dev:backend` — servidor backend em modo watch.
- `npm run dev:frontend` — inicia frontend (executar dentro de `frontend`).
- `npm run dev:ai` — executa o serviço Python de IA (`python backend/ai/core.py`).
- `npm test` — executa testes Jest; `npm run test:contracts` — executa testes Hardhat.

**Convenções do repositório**
- Usa ES modules (`type: module`) em todo o backend.
- Modelos Mongoose declaram explicitamente `collection` (ex.: `decisions`, `users`).
- Enum `recommendation` em `Decision` é `ACCELERATE|MONITOR|PAUSE` — código e UI dependem desses valores.
- Autenticação de desenvolvimento é simplificada: senhas em texto plano (TODOs em `backend/routes/auth.js`). Se alterar a semântica de autenticação, atualize testes em `backend/__tests__/`.
- Testes de integração usam `supertest` e assumem que a app é exportada como módulo utilizável por `supertest`.

**Quando fizer alterações**
- Mude rotas/formatos de API: atualize `backend/routes/*`, `backend/models/*` e testes em `backend/__tests__/*`.
- Novas rotas protegidas: envolver com `authMiddleware` (exportado em `backend/middleware/auth.js`).
- Ao alterar contrato/API de calibração IA: atualize `AI_SERVICE_URL` no backend e ajustes no `backend/ai/core.py` (e testes de integração, se houver).

**Exemplos de prompts úteis para o agente**
- "Atualize a rota `POST /api/decisions` para aceitar um novo campo `tags: string[]` e persistir no modelo `Decision` — atualize `backend/models/Decision.js`, `backend/routes/decisions.js` e adicione testes em `backend/__tests__/decisions.test.js`." 
- "Refatore `backend/routes/auth.js` para usar `bcrypt` ao salvar e comparar senhas; mantenha compatibilidade com os testes existentes (ou atualize-os)." 
- "Implemente a função de minting comentada (`TODO: Anchor to blockchain`) em `backend/routes/decisions.js` usando `ethers` e contrato `EvidenceNote.sol`. Crie um campo `blockchain_tx` com o hash da transação." 
- "Adicione um teste de integração que mocka o serviço de IA (`AI_SERVICE_URL`) para garantir que `POST /api/decisions` salva `omega_score` e `recommendation` corretamente." 

Quando escrever prompts, seja específico sobre arquivos a modificar, efeitos esperados (status codes, shapes JSON) e como validar localmente.

**Avisos e variáveis de ambiente**
- Não assuma que senhas estão hashed — o repositório contém notas TODO explícitas.
- Variáveis importantes: `MONGODB_URI`, `JWT_SECRET`, `AI_SERVICE_URL`, `PORT`, `POLYGON_*` (ver `.env` para exemplos).

Se algo estiver incompleto ou você quiser que eu expanda com exemplos de PR, comandos `gh` ou um checklist de revisão, diga qual parte deseja aprofundar.
