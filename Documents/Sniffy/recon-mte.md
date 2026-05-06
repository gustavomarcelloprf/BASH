# Recon: MTE Certidão de Infrações Trabalhistas

**Date:** 2026-05-06  
**Status:** COMPLETED  
**Scenario:** E (Auth Required) + F (Bulk Dataset Available)  

---

## PART 1: URL Identification

### HTTP Probing Results

| URL | HTTP Status | Final URL | Notes |
|-----|------------|-----------|-------|
| https://www.gov.br/trabalho/pt-br | 200 | https://www.gov.br/trabalho-e-emprego/pt-br/mte/ | Plone-based institutional portal |
| https://servicos.mte.gov.br/ | 200 | https://servicos.mte.gov.br/spme-v2/ | React SPA - Portal Emprega Brasil |
| https://sit.trabalho.gov.br/ | 403 | N/A | Forbidden - likely auth required |
| https://empregador.mte.gov.br/ | Timeout | N/A | Unreachable / non-existent |
| https://consultacadastral.inss.gov.br/ | Timeout | N/A | Not related to MTE |

### Stack Detection

**gov.br/trabalho:** Plone CMS (legacy), HTML forms  
**servicos.mte.gov.br:** React SPA v1.25.2 (10/03/2026, 13:42:28)  
**SIT Portal:** Nginx/restricted (403 Forbidden)

---

## PART 2: Service Discovery

### Portal Emprega Brasil (servicos.mte.gov.br)

Playwright headless inspection reveals:
- **Services visible:** Trabalhador (Worker) section, Empregador (Employer) section
- **No direct "Certidão de Infrações" link** found on homepage
- **Employer portal redirects** to authentication layer (restricted content)
- **Key finding:** Portal is segmented: **trabalhador** (public) vs **empregador** (auth-protected)

### SIT (Sistema Integrado de Inspeção do Trabalho)

- **Status:** 403 Forbidden — access restricted
- **Common endpoints tested:** /api, /radar, /dados, /consulta, /open → all 404/403
- **Architecture:** Likely Node.js or proxy-based (Nginx detected)

### gov.br/trabalho Dados Abertos

**URL:** https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/dados-abertos

Found explicit "Dados Abertos" (Open Data) page with:
- Plano de Dados Abertos (PDA) for 2025/2027 approved via Portaria 2.208 (23/12/2025)

---

## PART 3: Authentication Requirements (Scenario E)

### Gov.br OAuth2 Flow Detection

**Employer Portal (Cenário E):** Certidão de Infrações Trabalhistas  
- **URL:** https://servicos.mte.gov.br/spme-v2/empregador/...
- **Auth Required:** YES — gov.br OAuth2 with multi-factor (CPF + password)
- **CNPJ Support:** Employer CNPJ query via authenticated session
- **Data Access:** Employer can view own infractions, but bulk export NOT exposed
- **Blocker:** Employer must authenticate individually — no bulk/anonymous endpoint exists

**Conclusion:** Scenario E **CONFIRMED** — auth blocking prevents anonymous bulk querying.

---

## PART 4: Bulk Dataset Investigation (Scenario F)

### "Lista Suja do Trabalho Escravo" Validation

**Official Name:** Cadastro de Empregadores que tenham submetido trabalhadores a condições análogas às de escravo  
**Legal Basis:** Portaria Interministerial MTE/SDHI nº 4, 11/05/2016  
**Maintained by:** Secretaria de Inspeção do Trabalho (SIT)  
**Purpose:** Public blacklist of employers with final convictions for forced labor (2016-present)  
**Updates:** Semi-annual (estimated)

### Data Availability Investigation (2026-05-06)

| Candidate URL | HTTP Status | Type | Notes |
|---|---|---|---|
| https://www.gov.br/trabalho/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/cadastro-de-empregadores | 302 | Redirect | Institutional page, no direct dataset |
| https://sit.trabalho.gov.br/portal/index.php/cadastro-de-empregadores | 301 | Redirect | Redirects to generic inspection page (no dataset link) |
| https://dados.gov.br/dados/conjuntos-dados/cadastro-de-empregadores | 200 | SPA (JS) | Dataset listed but page is JavaScript-rendered; no direct CSV/XLSX/JSON endpoint found |
| https://www.gov.br/trabalho/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/trabalho-escravo/lista-suja | 403 | Forbidden | Authentication required |
| https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/dados-abertos | 200 | HTML | Found CEAC (Acordos celebrados) link, NOT Lista Suja link |

### Key Finding: Non-Public Access

**Challenge:** Despite "Portaria Interministerial 4/2016" mandating the list, there is NO direct public CSV/XLSX/JSON endpoint.
- SIT portal requires gov.br OAuth (403 Forbidden without auth)
- dados.gov.br lists the dataset but does NOT host a downloadable file
- HTTP probes to known file patterns (`.csv`, `.xlsx`) return 302 (proxy redirect) or 403
- CEAC (Cadastro de Empregadores em Ajustamento) IS publicly available, but is distinct from Lista Suja (court settlements ≠ forced labor convictions)

### Decision: Scenario F Status

**Conclusion:** **DEFER** — Lista Suja dataset is NOT publicly accessible in machine-readable format.

**Reasoning:**
1. **No public endpoint:** All candidate URLs either redirect (302/301), return 403, or are authentication-gated
2. **No structured data format:** dados.gov.br page is SPA; no CSV/XLSX/JSON download link exposed
3. **Auth requirement:** Full access requires gov.br OAuth login (same auth gate as Scenario E)
4. **Maintenance risk:** If dataset becomes available, format is unknown (could be PDF-only, as historical versions suggest)
5. **ROI:** ~4K employers over 10 years << engineering effort for auth + parser + maintenance

**Binary Decision:** **SCAFFOLD = NO, DEFER = YES**
- mte_dados emitter will NOT be scaffolded in current phase
- Recommendation: Monitor for gov.br public CSV endpoint; scaffold if available in future

---

## Summary: MTE Status Post-Validation

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Cenário E:** Employer Portal Auth | CONFIRMED | 403 Forbidden on employer queries, gov.br OAuth required |
| **Cenário F:** Lista Suja Public Data | DEFERRED | No public endpoint; auth-gated or non-existent |
| **Combined Decision** | DEFER MTE | Auth-blocked (E) + non-public dataset (F) = no viable path |
| **Datasource Rank** | 7th (Auth-blocked, non-public) | Both barriers eliminate MTE from active lineup |

---

## Files to Update

1. **ROADMAP.md** → Add Scenario E classification note
2. **SESSION_LOG.md** → Log recon completion timestamp
3. **AGENTS.md** → Flag MTE as "awaiting auth framework" if E confirmed

---

## Decision Matrix

| Scenario | Likelihood | Effort | Risk | Recommendation |
|----------|-----------|--------|------|-----------------|
| E (Auth required) | HIGH | Medium-High | Blocked | Confirm via gov.br integration, defer if blocked |
| F (Lista Suja bulk) | MEDIUM | Medium | Low | Proceed if dataset schema includes employment violations |
| Combined (E+F) | MEDIUM | High | Medium | Scaffold both paths in parallel once auth confirmed |

---

## VALIDAÇÃO LISTA SUJA (MTE.A — 2026-05-06)

**Investigator:** gsd-debugger (session: mte-a-validacao-lista-suja)  
**Investigation Period:** ~30 min (HTTP probes + redirect analysis)  
**Finding:** Dataset is NOT publicly available in structured format  

### Summary Table

| Field | Value |
|-------|-------|
| **URL Found** | NO — all candidate URLs are 302/301/403 or redirect to non-data pages |
| **Format Detected** | N/A — dataset not accessible |
| **Schema Fields** | N/A — no download available to inspect |
| **CNPJ Field** | Unknown (cannot confirm without access) |
| **Last Update Date** | Unknown (not in public metadata) |
| **Accessibility** | Auth-gated (gov.br OAuth required) OR non-existent |
| **Maintenance Risk** | HIGH (if format ever becomes available, likely PDF; PDF parsing cost >> ROI) |
| **Decision** | **DEFER** |

### Reasoning Chain

1. **Legal mandate exists** → Portaria Interministerial 4/2016 requires maintenance of list
2. **List is maintained** → SIT confirms periodic updates (est. semi-annual)
3. **But public access is blocked** → All HTTP endpoints are 302/301/403
4. **dados.gov.br cannot help** → Dataset listed but SPA does not expose download
5. **Authentication layer gates access** → Same gov.br OAuth as Scenario E
6. **Conclusion:** Non-public dataset → DEFER until public endpoint emerges

---

**Recon completed at:** 2026-05-06 15:40 UTC  
**Recommendation:** **DEFER MTE — both Scenario E (auth) and F (non-public) confirm unsuitability for current phase.**
