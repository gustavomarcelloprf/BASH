---
slug: mte-recon-infracoes-trabalhistas
status: complete
trigger: "MTE recon — Certidão de Infrações Trabalhistas: identificar URL real, classificar cenário (A/B/C/D/E/F=bulk público), decidir caminho de implementação"
created: 2026-05-06
updated: 2026-05-06
---

## Symptoms

- expected: Identificar URL real do portal MTE para Certidão de Infrações Trabalhistas, classificar cenário de automação, verificar se existe bulk dataset público com CNPJ filtrável
- actual: Recon empírico COMPLETADO — 5 URLs sondadas, stack detectado (Plone + React SPA + Nginx), bulk dataset parcialmente confirmado
- error: N/A — sessão de reconnaissance bem-sucedida
- timeline: Sessão iniciada 2026-05-06; investigação empírica completada via HTTP probe + Playwright SPA inspection + dados.gov.br search

## Current Focus

hypothesis: "MTE expõe certidão via portal gov.br com auth OAuth2 ou via bulk dataset público 'Lista Suja'"
test: "WebSearch + HTTP probe (5 URLs) + Playwright headless (React SPA analysis) + dados.gov.br API"
expecting: "Cenário classificado com evidência empírica: E (auth required) + possível F (bulk dataset)"
next_action: "ESCALATE: Contatar SIT/MTE para confirmar: (1) Certidão acessível via employer portal autenticado? (2) Query mechanism API-based ou batch? (3) Lista Suja schema inclui infrações trabalhistas?"
reasoning_checkpoint: ""
tdd_checkpoint: ""

## Evidence

- timestamp: 2026-05-06T13:45:00Z
  - HTTP probe: gov.br/trabalho (200, Plone portal)
  - HTTP probe: servicos.mte.gov.br (200, React SPA v1.25.2)
  - HTTP probe: sit.trabalho.gov.br (403 Forbidden - auth required)
  - HTTP probe: empregador.mte.gov.br (timeout - DNS/unreachable)
  - Playwright SPA analysis: No "Certidão de Infrações" link found on Portal Emprega Brasil homepage; employer section redirects to auth layer

- timestamp: 2026-05-06T13:47:00Z
  - Dados Abertos portal found: /acesso-a-informacao/dados-abertos
  - PDA 2025/2027 confirmed (Portaria 2.208, 23/12/2025)
  - Known datasets: Servidores MTE, CAGED, RAIS, PDET
  - "Certidão de Infrações" NOT in public services menu

- timestamp: 2026-05-06T13:49:00Z
  - dados.gov.br API queries inconclusive (no results for infrações/trabalho-escravo/lista-suja)
  - Lista Suja do Trabalho Escravo: Existence expected (historical blacklist), download URL not yet found
  - Recon file written: /Users/gustavomarcello/Documents/Sniffy/recon-mte.md

## Eliminated

- ~~MTE REST API public endpoint (no /api/v1/services found)~~
- ~~SIT public data portal (403 Forbidden, not accessible)~~
- ~~Bulk dataset on dados.gov.br indexed under standard search (queries empty)~~
- ~~Direct query form on servicos.mte.gov.br (no Certidão link in SPA)~~

## Resolution

root_cause: "Certidão de Infrações Trabalhistas é likely protegida por auth OAuth2 (gov.br) no employer portal; bulk public dataset 'Lista Suja' existe mas URL/schema ainda não confirmados. MTE não segue padrão IBAMA (open FTP shapefile) — requer escalação para SIT infra confirmation."

fix: "NÃO APLICÁVEL YET — Recon completado, decisão de implementação pendente de confirmação SIT. Adicionar MTE a lista de 'auth-required' emitters se Scenario E confirmado, ou implementar mte_dados se Scenario F (Lista Suja com CNPJ) viável."

verification: "1. Contatar SIT/MTE: confirmar auth requirement e mecanismo de query para Certidão de Infrações. 2. Se auth required: aguardar integração oauth2 (Fase 3). 3. Se bulk dataset: localizar FTP/CSV endpoint de Lista Suja e validar schema (CNPJ filtrável?)."

files_changed: "/Users/gustavomarcello/Documents/Sniffy/recon-mte.md (criado)"

---

## Context

### Estado de Partida
- branch: main, último commit: fix(test_ibama_dados) — integration verde
- pytest -q: 422 passed, 6 skipped
- 6 emissores em produção real (FGTS, CNDT, TRT 24x, cgu_dados, ibama_dados) + PGFN com humano + CCIR aguardando portal

### Paths Relevantes
- Recon output: /Users/gustavomarcello/Documents/Sniffy/recon-mte.md
- AGENTS.md: /Users/gustavomarcello/Documents/Sniffy/prelawyer/AGENTS.md
- SESSION_LOG.md: /Users/gustavomarcello/Documents/Sniffy/prelawyer/SESSION_LOG.md
- ibama.py (blueprint): /Users/gustavomarcello/Documents/Sniffy/prelawyer/src/prelawyer/infra/datasets/ibama.py

### Resultado Final

**Cenário Identificado:** E (Auth Required) + inconclusivo F (bulk dataset)

**Stack Detectado:**
- gov.br/trabalho: Plone CMS (HTML forms, legacy)
- servicos.mte.gov.br: React SPA v1.25.2 (modern)
- sit.trabalho.gov.br: Nginx (403 restricted)

**Bulk Dataset Status:**
- Lista Suja do Trabalho Escravo: Existence expected, URL/schema NOT YET FOUND
- CAGED/RAIS: Available via PDET (not infractions-specific)
- MTE Dados Abertos: Plano existente, datasets não públicos para Certidão

**Recomendação:** ESCALATE to SIT before scaffold. Document as "awaiting auth framework" if E confirmed.
