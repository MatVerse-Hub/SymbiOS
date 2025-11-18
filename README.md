# SymbiOS

Ponte entre a intenção humana e a execução tecnológica, com um backend Express modular, serviço de IA em FastAPI e contratos prontos para integração.

## Como rodar

### Backend (Express)

```bash
cd backend
npm install
npm run dev
# testes e lint
npm test
npm run lint
```

Para a API de IA local (FastAPI):

```bash
cd backend/ai
pip install -r requirements.txt
pytest  # opcional para checar a suíte mínima
python core.py  # sobe em http://localhost:8000
```

### Contratos (Hardhat)

```bash
cd contracts
npm install
npm run lint
npm run test
npm run compile
```

### Variáveis de ambiente

Veja `.env.example` para os valores esperados. Configure `MONGODB_URI`, `JWT_SECRET` e `AI_SERVICE_URL` antes de subir em produção.

## Rotas principais

- `POST /api/auth/login` — autenticação simplificada, retorna JWT.
- `POST /api/decisions` — protegido por JWT. Chama o serviço de IA (`/calibrate`) e persiste a decisão.
- `GET /api/decisions` — lista as últimas decisões do usuário autenticado.

## Scripts

- `npm run dev:backend` — backend Express com watch.
- `npm run dev:ai` — serviço de IA em Python (FastAPI).
- `npm test` — testes Jest com supertest.

## Licença

MIT
