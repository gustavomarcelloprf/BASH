# DASH

App web mobile-first para rastreio de horas em escritório jurídico via linguagem natural.

## Rodando localmente

```bash
# Backend
cd backend
cp .env.production.example .env   # edite com suas variáveis
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py
.venv/bin/uvicorn app.main:app --reload   # http://localhost:8000

# Frontend (outro terminal)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

Usuários de teste: `admin@dash.local / dash123` e `dev@dash.local / dash123`.

## Deploy

**Backend → Railway:** conecte o repositório, adicione um serviço PostgreSQL (DATABASE_URL é injetada automaticamente) e configure as variáveis abaixo. O `railway.toml` já configura build e healthcheck.

```
SECRET_KEY=<openssl rand -hex 32>
OPENAI_API_KEY=<opcional>
ACCESS_TOKEN_EXPIRE_HOURS=24
DEBUG=false
```

**Frontend → Vercel:** importe o repositório com Root Directory = `frontend`. Adicione:

```
VITE_API_URL=https://<seu-projeto>.railway.app
```

O `vercel.json` já configura o rewrite para SPA.

## Importando dados históricos

Exporte do Google Sheets como `.xlsx` (Arquivo → Fazer download → Excel).
Colunas esperadas: `Data`, `Nome`, `Projeto`, `Horas`.

```bash
curl -X POST https://<api>/api/import/excel \
  -H "Authorization: Bearer <token>" \
  -F "file=@planilha.xlsx"
```

## Estrutura do projeto

```
.
├── backend/
│   ├── app/
│   │   ├── models/       User, Project, TimeEntry
│   │   ├── routers/      auth, entries, dashboard, imports
│   │   └── services/     parser, importer, normalizer, roi
│   ├── scripts/          create_user.py
│   ├── tests/
│   └── railway.toml
└── frontend/
    ├── src/
    │   ├── components/   MetricsBar, ChatInput, EntryList, AlertList, Toast
    │   ├── hooks/        useAuth, useEntries, useParser, useDashboard, useAlerts
    │   ├── pages/        Login, Home
    │   └── stores/       auth, toast
    └── vercel.json
```
