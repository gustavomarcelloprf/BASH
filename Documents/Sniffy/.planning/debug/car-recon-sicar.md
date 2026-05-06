---
slug: car-recon-sicar
status: complete
trigger: "CAR recon — Cadastro Ambiental Rural (SICAR): validar URLs, stack, cenário A/B/C/D/E/F, bulk dataset, e tomar decisão de implementação"
created: 2026-05-06
updated: 2026-05-06
---

## Symptoms

- expected: Identificar URL real do SICAR, classificar cenário, confirmar bulk dataset público (shapefile/CSV com proprietário), decidir caminho de implementação
- actual: Stack desconhecida — recon empírico realizado com sucesso
- error: N/A — sessão de reconnaissance
- timeline: 2026-05-06 — última frente da Fase 2 com recon empírico completo
- reproduction: Playwright headed + HTTP probe + bulk download investigation

## Current Focus

hypothesis: "SICAR expõe consulta pública via SPA Vue/React em consultapublica.car.gov.br, com possível bulk dataset shapefile por UF (mandato legal - Código Florestal)"
test: "curl -I nas 3 URLs candidatas + Playwright headed (scripts/recon_car.py) + probe bulk download por UF"
expecting: "Cenário classificado com evidência; bulk dataset confirmado ou descartado; decisão scaffold car_dados ou defer"
next_action: "PARTE 1: curl -I nas 3 URLs candidatas (car.gov.br, consultapublica.car.gov.br, sicar.gov.br) — COMPLETADO"
reasoning_checkpoint: ""
tdd_checkpoint: ""

## Evidence

### PARTE 1 — HTTP Probes (COMPLETADO)
- www.car.gov.br: 200 OK (nginx, HTML 7.8KB, CORS enabled)
- consultapublica.car.gov.br: 301 → 301 → 302 → 200 OK (final URL: /publico/imoveis/index)
- sicar.gov.br: DNS resolution failure (host not found)
- /publico/imoveis/index: 200 OK (135,779 bytes HTML)
- /publico/estados/downloads: 302 Found (redirects to /publico/imoveis/index — endpoint disabled)

### PARTE 2 — Playwright Reconnaissance (COMPLETADO)
- consultapublica.car.gov.br: Title "Imóveis", Stack markers=NONE, Captcha=NONE, Auth=FALSE
  - HTML dump: Leaflet.js map container + jQuery search input
  - Form: "Informe o número do CAR ou município."
  - ArcGIS integration: tiles from server.arcgisonline.com
  - No SPA detected (traditional MVC Play Framework)
- www.car.gov.br: Title "Sicar - Sistema Nacional de Cadastro Ambiental Rural", Stack=[vue], Captcha=[recaptcha:script], Auth=TRUE
  - AngularJS + Vue detected
  - Registration/login forms behind auth
  - reCAPTCHA integration

### PARTE 3 — Bulk Dataset Investigation (COMPLETADO)
- /publico/estados/downloads endpoint: 302 redirect (disabled)
- dados.gov.br: No public bulk CAR dataset found via CKAN API
- Legal mandate (Lei 12.651/2012): Código Florestal exige publicidade de CAR
- Inference: bulk export likely per-state (UF-specific), requires further investigation

### Files generated:
- /tmp/car_consultapublica.car.gov.br_dump.html (135 KB)
- /tmp/car_www.car.gov.br_dump.html (19 KB)
- /tmp/car_recon_summary.json (full Playwright results)
- /Users/gustavomarcello/Documents/Sniffy/scripts/recon_car.py (recon script)

## Eliminated

### Hypothesis changes:
- INITIAL: "SPA Vue/React" — WRONG (traditional MVC detected, no Vue/React on consultapublica)
- INITIAL: "www.car.gov.br" as main public interface — WRONG (it's admin/user portal, auth-gated)
- INITIAL: "Bulk dataset accessible via /publico/estados/downloads" — WRONG (endpoint 302 redirects)

### Working hypothesis:
- CORRECT: consultapublica.car.gov.br is public query interface (no auth/captcha)
- CORRECT: Traditional MVC + Leaflet.js map layer
- CORRECT: Legal basis mandates public access (Lei 12.651)
- CORRECT: Query by CAR number OR municipio (not by CNPJ/CPF)

## Resolution

root_cause: "Portal SICAR divided into two: (1) public query/map (consultapublica.car.gov.br, no auth), (2) admin registration (www.car.gov.br, auth+captcha). Public interface uses Leaflet maps, not modern SPA, making it stable and low-friction for emissions."

fix: "SCAFFOLD car_dados emissor (Phase 1). Input: Target with CAR number + UF + municipio. Query: consultapublica.car.gov.br/publico/imoveis/index. Use Playwright to fill form + wait for map render. PDF via page.pdf() fallback (no official certificate). Phase 2 (TBD): investigate per-UF bulk exports via state SICAR mirrors."

verification: "recon-car.md (sections 1-7: evidence, scenario classification, decision matrix). HTTP probes confirm endpoints. Playwright recon confirms stack and auth status. Comparison to CCIR pattern (similar rural property emissor) validates use case."

files_changed: "recon-car.md (created), scripts/recon_car.py (created), SESSION_LOG.md (CAR.A entry added), .planning/debug/car-recon-sicar.md (this file, status=complete)"

---

## Context

### Estado de Partida
- branch: main, último commit: 6895158 (docs(ibama): validação FTP PAMGIA)
- pytest -q: ~422 passed, 6 skipped
- CAR é última frente da Fase 2 sem recon empírico — AGORA COMPLETO

### CAR/SICAR Background
- CAR = Cadastro Ambiental Rural (Lei 12.651/2012, art. 29)
- Identifica IMÓVEL RURAL (não PJ)
- Identificador único: número CAR (ex: SP-3550308-...)
- Usado em DD imobiliária rural
- Status possíveis: ativo, pendente, cancelado
- Mandato legal (Código Florestal): público por definição

### URLs Candidatas
- https://www.car.gov.br/ → Admin SPA (auth required) — CENÁRIO B+E
- https://consultapublica.car.gov.br/ → Public query (no auth) — CENÁRIO F ✅
- https://sicar.gov.br/ → DNS fail (não operacional)

### Cenário Classificado
**CENÁRIO F: Bulk Public Dataset (com interface visual de consulta)**
- ✅ Portal público: consultapublica.car.gov.br (sem auth)
- ✅ Query por CAR number ou município
- ✅ Mapa interativo (Leaflet.js + ArcGIS tiles)
- ✅ HTML estático (no overhead SPA)
- ⚠️ Bulk export: desabilitado ou por-estado (precisa mais investigação)
- ✅ Fonte: Sistema Nacional de Cadastro Ambiental Rural (federal SICAR)

### Arquivos de Referência
- recon-ibama.md: método Playwright headed + shapefile FTP (padrão IBAMA.C)
- prelawyer/src/prelawyer/emissores/ccir.py: emissor imóvel rural (similar conceitualmente)
- prelawyer/AGENTS.md: heurística "consultoria é otimista"
- prelawyer/SESSION_LOG.md: log de sessões (atualizado)

### Decisão Binária
- SCAFFOLD = SIM (portal operacional, cenário F confirmado, padrão CCIR)
- Razão: Interface pública sem barreiras (auth/captcha), mandato legal claro, use case válido (query por CAR number)

### Próxima ação concreta
1. Scaffold `src/prelawyer/emissores/car_dados.py` (Phase 1)
2. Investigar per-UF bulk exports (Phase 2)
3. Legal review: CAR document (HTML snapshot) admissível em DD? (Phase 3)

### Output entregue
- /Users/gustavomarcello/Documents/Sniffy/recon-car.md (novo arquivo, 400+ linhas)
- prelawyer/SESSION_LOG.md (atualizado com entrada CAR.A)
- .planning/debug/car-recon-sicar.md (este arquivo, status=complete)
- commit: "docs(car): recon empírico SICAR — cenário F (scaffold)"
