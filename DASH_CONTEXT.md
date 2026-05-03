# DASH — Contexto da Sessão

## O que é o DASH
App web mobile-first para rastreio de horas em escritório jurídico.
Usuários digitam em linguagem natural ("2h na petição do caso Silva"),
um parser extrai os dados e um dashboard exibe métricas e alertas de budget.

## Estrutura de pastas
```
~/
├── backend/        FastAPI + SQLModel + SQLite
└── frontend/       React 18 + TypeScript + Tailwind + Vite
```

## Backend (backend/)

### Como rodar
```bash
cd backend
.venv/bin/uvicorn app.main:app --reload  # porta 8000
.venv/bin/python3 seed.py               # popula com dados de teste
.venv/bin/python3 -m pytest tests/ -v  # 24 testes, todos verdes
```

### Stack
- Python 3.14, FastAPI 0.111, SQLModel, pydantic-settings
- passlib[bcrypt] (bcrypt<4.0.0 — compatibilidade Python 3.14)
- rapidfuzz, pandas, openpyxl, openai

### Módulos implementados
| Arquivo | Responsabilidade |
|---|---|
| `app/models/user.py` | User (id, email, hashed_password, role, hourly_rate) |
| `app/models/project.py` | Project (name, budget_hours, hourly_rate, status) |
| `app/models/entry.py` | TimeEntry (project_id, user_id, date, hours, source, is_active) |
| `app/routers/auth.py` | POST /api/auth/login, GET /api/auth/me, JWT HS256 |
| `app/routers/entries.py` | CRUD /api/entries + POST /api/entries/parse |
| `app/routers/imports.py` | POST /api/import/excel (multipart .xlsx) |
| `app/routers/dashboard.py` | GET /api/dashboard/summary|alerts|roi |
| `app/services/normalizer.py` | normalize_project_name() com rapidfuzz threshold 85% |
| `app/services/importer.py` | import_xlsx() pipeline completo |
| `app/services/parser.py` | parse_regex() + parse_llm() + parse() orquestrador |
| `app/services/roi.py` | calculate_roi(entries_count) — 4 min/entrada |

### Usuários de teste (seed)
- admin@dash.local / dash123 (role=admin)
- dev@dash.local   / dash123 (role=member)

### Endpoints ativos
```
GET  /health
POST /api/auth/login
GET  /api/auth/me
GET  /api/entries?period=month
POST /api/entries
PUT  /api/entries/{id}
DELETE /api/entries/{id}          ← soft delete (is_active=False)
POST /api/entries/parse           ← preview sem salvar
POST /api/import/excel
GET  /api/dashboard/summary?period=month|week|custom
GET  /api/dashboard/alerts
GET  /api/dashboard/roi
```

## Frontend (frontend/)

### Como rodar
```bash
cd frontend
npm install
npm run dev   # porta 5173
```

### Stack
- React 18, TypeScript, Tailwind 3, Vite 5
- @tanstack/react-query@5, zustand@4, axios, use-debounce, react-router-dom@6

### Estrutura src/
```
types/index.ts          User, Project, TimeEntry, ParseResult, DashboardSummary
stores/auth.ts          Zustand + sessionStorage (não localStorage)
lib/api.ts              axios + interceptor JWT + redirect 401→/login
hooks/
  useAuth.ts            login mutation + navigate /
  useEntries.ts         CRUD + optimistic delete
  useParser.ts          debounce 300ms, enabled >3 chars
  useDashboard.ts       refetch 30s
  useAlerts.ts          refetch 60s
components/
  MetricsBar/           dados reais + skeleton animado
  ChatInput/            input + LivePreview em tempo real
  EntryList/            lista + botão × optimistic
  AlertList/            barra progresso cinza/preto, warning vs critical
pages/
  Login.tsx             form email/senha
  Home.tsx              MetricsBar sticky + ChatInput + AlertList (condicional) + EntryList
```

### Paleta (só preto/branco/cinzas)
`#111 #333 #666 #999 #aaa #e5e5e5 #f0f0f0 #f9f9f9 #fff`

### Fluxo end-to-end funcionando
1. Login → token no sessionStorage → redireciona /
2. Digitar → useParser debounce 300ms → LivePreview: "2h · petição caso Silva · hoje"
3. Enter → POST /api/entries → invalida query → EntryList atualiza sem reload
4. × → optimistic remove → DELETE /api/entries/{id}
5. MetricsBar exibe dados reais a cada 30s
6. AlertList aparece quando projeto ≥80% do budget (só preto/cinza)

## O que NÃO foi implementado ainda (próximas semanas)
- Celery/Redis para processamento assíncrono do xlsx
- SSE para progresso de import
- Tela de cadastro de usuários
- Gráficos (Recharts)
- Geração de PDF
- Dark mode
- Alembic migrations (usa create_db_and_tables() por enquanto)

## Decisões técnicas notáveis
- `import_xlsx` é **síncrono** — async vem com Celery
- Deduplicação por chave `(user_id, project_id, date, hours)` em memória
- Parser: regex roda sempre; LLM só se OPENAI_API_KEY configurada
- bcrypt<4.0.0 necessário por incompatibilidade com Python 3.14
- Soft delete em TimeEntry via `is_active=False`
