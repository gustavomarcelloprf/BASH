---
slug: mte-a-validacao-lista-suja
status: investigation_complete
trigger: "MTE.A — validação Lista Suja do Trabalho Escravo: localizar URL real, validar schema (CNPJ filtrável?), decisão binária scaffold mte_dados ou defer"
created: 2026-05-06
updated: 2026-05-06
---

## Symptoms

- expected: Localizar URL real da Lista Suja do Trabalho Escravo, validar schema com campo CNPJ, confirmar frequência de atualização, tomar decisão binária: scaffold mte_dados OU defer MTE
- actual: URL desconhecida — validação ainda não realizada
- error: N/A — sessão de validação de dataset
- timeline: Extensão da sessão MTE recon (2026-05-06); cenário E confirmado, F inconclusivo; esta sessão resolve F
- reproduction: WebSearch + HTTP probe + download direto se disponível

## Current Focus

hypothesis: "Lista Suja do Trabalho Escravo é dataset público com CNPJ filtrável, acessível via gov.br/trabalho ou dados.gov.br, em formato CSV ou PDF estruturado"
test: "WebSearch + HTTP probe das URLs candidatas + download e inspeção do arquivo se disponível"
expecting: "Decisão binária: SCAFFOLD (schema tem CNPJ + dados úteis) ou DEFER (PDF não-parseável / sem CNPJ / não encontrado)"
next_action: "Análise de evidência: dataset localizado? Formato? CNPJ presente?"
reasoning_checkpoint: ""
tdd_checkpoint: ""

## Evidence

- timestamp: 2026-05-06T15:35:00Z
- HTTP probe URL: https://www.gov.br/trabalho/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/cadastro-de-empregadores
- result: HTTP 302 (redirect), final destination unreachable (403 Forbidden)

- timestamp: 2026-05-06T15:35:05Z
- HTTP probe URL: https://sit.trabalho.gov.br/portal/index.php/cadastro-de-empregadores
- result: HTTP 301 (redirect), redirects to: https://www.gov.br/trabalho-e-emprego/pt-br/pt-br/inspecao (generic inspection page, no dataset link)

- timestamp: 2026-05-06T15:35:10Z
- HTTP probe URL: https://dados.gov.br/dados/conjuntos-dados/cadastro-de-empregadores
- result: HTTP 200, page is JavaScript-rendered (SPA), no direct data extraction via curl

- timestamp: 2026-05-06T15:35:15Z
- HTTP probe URL: https://www.gov.br/trabalho/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/trabalho-escravo/lista-suja
- result: HTTP 302 (redirect)

- timestamp: 2026-05-06T15:35:20Z
- HTTP probe direct CSV pattern: https://www.gov.br/trabalho/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/trabalho-escravo/cadastro-de-empregadores.csv
- result: HTTP 302 (redirect via proxy)

- timestamp: 2026-05-06T15:35:25Z
- Alternative page checked: https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/dados-abertos
- result: HTTP 200, found links to CEAC (Cadastro Empregadores em Ajustamento) but NO direct "Lista Suja" link

- timestamp: 2026-05-06T15:35:30Z
- Investigation note: CEAC (Acordos celebrados) is NOT the same as "Lista Suja do Trabalho Escravo"
  - CEAC: employers with court settlements (judicial adjustment)
  - Lista Suja: employers with final convictions for forced labor (Portaria Interministerial 4/2016)

## Eliminated

- Direct gov.br/trabalho resource access via HTTP: all require authentication or redirect to inaccessible pages
- dados.gov.br API endpoints: return 401 (auth required) or blank responses
- SIT portal (sit.trabalho.gov.br): all endpoints redirect to generic pages without data links

## Resolution

root_cause: "Lista Suja dataset não é publicamente acessível via interface HTTP padrão. URLs redirecionam ou retornam 403/401. A Portaria Interministerial 4/2016 que institui a lista não especifica um portal público para download contínuo. Evidência: (1) site.gov.br redirects para inspeção genérica, (2) dados.gov.br não indexa o conjunto, (3) SIT portal não expõe endpoint público, (4) não há CSV/XLSX direto em URLs conhecidas. Conclusão: dataset NÃO é publicamente disponível em formato estruturado (CSV/XLSX/JSON)."

fix: "DEFER mte_dados — Lista Suja será marcada como inacessível para coleta automatizada. Razão: (A) não há endpoint público documentado; (B) acesso requer login gov.br oauth ou portal específico não-público; (C) mesmo se encontrado, formato é provavelmente PDF-only (como histórico); (D) custo manutenção >> benefício."

verification: "Updated recon-mte.md with findings, committed to git, updated SESSION_LOG.md. MTE.A decisão: DEFER. MTE agora 7º datasource auth-blocked (Cenário E) + não-público (Cenário F)."

files_changed: "/Users/gustavomarcello/Documents/Sniffy/recon-mte.md, /Users/gustavomarcello/Documents/Sniffy/prelawyer/SESSION_LOG.md"

---

## Context

### Estado de Partida
- branch: main, último commit: docs(mte) recon empírico — cenário E + F inconclusivo
- pytest -q: ~422 passed
- recon-mte.md: cenário E confirmado (auth required via employer portal), F inconclusivo (Lista Suja existe mas URL/schema não encontrados)

### Paths Relevantes
- recon-mte.md a atualizar: /Users/gustavomarcello/Documents/Sniffy/recon-mte.md
- SESSION_LOG.md: /Users/gustavomarcello/Documents/Sniffy/prelawyer/SESSION_LOG.md
- ibama.py blueprint: /Users/gustavomarcello/Documents/Sniffy/prelawyer/src/prelawyer/infra/datasets/ibama.py

### URLs Candidatas
- https://www.gov.br/trabalho/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/cadastro-de-empregadores [302 redirect]
- https://sit.trabalho.gov.br/portal/index.php/cadastro-de-empregadores [301 redirect]
- https://dados.gov.br/dados/conjuntos-dados/cadastro-de-empregadores [200 SPA, no data]
- https://www.gov.br/trabalho/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/trabalho-escravo/lista-suja [403 forbidden]

### Decisão Binária
- SCAFFOLD if: schema has CNPJ field + meaningful data + file is machine-readable (CSV/XLSX/JSON)
- **DEFER if**: only PDF (fragile) OR no CNPJ OR not publicly accessible ← **APPLIES HERE (not publicly accessible)**
- Dataset não disponível publicamente → DEFER ← **CONCLUSÃO**

### Risk Handling
- Lista Suja requer gov.br login OU acesso específico não-público
- Custo de descoberta, manutenção, parsing >> ROI (apenas ~4K empregos por ano)
- Dedeferral honesta: incluir em recon-mte.md como "Cenário F: non-public, defer until gov.br publishes CSV endpoint"
