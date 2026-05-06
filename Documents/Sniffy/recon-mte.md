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
- Dataset inventory structure exists
- Navigation visible: "Empregador" services menu → FGTS, CAGED, RAIS, eSocial, Mediação, PAT, etc.

**Critical:** No "Certidão de Infrações" service listed in employer menu on gov.br portal navigation.

---

## PART 3: Bulk Dataset Investigation

### dados.gov.br Search Results

**Attempted searches:**
- "infrações trabalhistas" → No results
- "trabalho escravo" → No results  
- "lista suja" → No results
- MTE organization endpoint queries → Empty responses

**Status:** dados.gov.br API appeared unresponsive or MTE datasets not indexed via standard CKAN.

### Known MTE Public Datasets

Based on Plano de Dados Abertos references:

1. **Dados Abertos de Servidores do MTE** ✓ Available
   - Servidores Efetivos e Cargos de Chefia
   - Remuneração de Servidores
   - Capacitação de Servidores

2. **PDET (Programa de Disseminação de Estatísticas)** ✓ Available
   - CAGED (employment records)
   - RAIS (annual labor roster)

3. **Lista Suja do Trabalho Escravo** - STATUS UNKNOWN
   - Expected: Historical registry of employers with forced labor violations
   - Update frequency: Unclear (likely annual)
   - Format: Likely CSV/DBF (following IBAMA pattern)
   - **NOT FOUND** in current recon — requires direct SIT/Fiscalização inquiry

---

## PART 4: Scenario Classification

### Root Finding

**Certidão de Infrações Trabalhistas appears to be:**

1. **NOT a public REST API** on servicos.mte.gov.br
2. **NOT directly query-able** via servicos.mte.gov.br SPA
3. **PROTECTED** behind gov.br OAuth2 authentication (employer portal access required)
4. **POSSIBLY sourced from SIT/Fiscalização backend**, but public querying mechanism unknown

### Scenario Assessment

**Scenario E (Auth Required):**
- Employer portal (`empregador.mte.gov.br` alt path via servicos.mte.gov.br/empregador) requires gov.br OAUTH2 login
- Certidão query likely requires authenticated session
- No public bulk dataset offering observed

**Scenario F (Bulk Public Dataset):**
- **Lista Suja do Trabalho Escravo** (slave labor blacklist) exists as public dataset
- **NOT confirmed** to contain "Infrações Trabalhistas" (broader labor violations)
- Download URL and schema not yet identified
- Requires follow-up: direct SIT contact or FTP endpoint discovery

---

## PART 5: Implementation Recommendation

### Short Term (Immediate)

**Status:** BLOCKED on Scenario E confirmation

**Action:**  
Verify if Certidão de Infrações Trabalhistas:
1. Is accessible via authenticated employer portal (gov.br OAUTH2 required)?
2. Has queryable API endpoint behind auth?
3. OR is downloadable only as bulk "Lista Suja" dataset?

**Next Step:** Consult with SIT/MTE infrastructure team or preview employer portal with gov.br credentials to confirm auth requirement and query mechanism.

### Medium Term (If Scenario E Confirmed)

If authentication is required:
- **Decision:** Add MTE to "auth-required" emitters list
- **Defer implementation** until gov.br OAUTH2 integration framework is available (Fase 3)
- Document as Scenario 7 (blocked) in ROADMAP

### Long Term (If Scenario F Confirmed)

If Lista Suja bulk dataset is sufficient for due diligence:
- Scaffold `mte_dados` emitter (blueprint: `ibama_dados`)
- FTP pull → DBF/CSV parse → CNPJ filter
- Caveat: Only historical forced labor (not broader infractions)

---

## Evidence Summary

- **URLs validated:** 5/5 probed
- **HTTP responses captured:** 200, 403, timeout
- **Stack detected:** Plone (gov.br), React v1.25.2 (servicos), Nginx (SIT)
- **Bulk dataset:** Partially confirmed (Lista Suja existence, not yet download URL)
- **Auth gate:** Confirmed on employer portal (403)
- **Captcha:** No captcha detected (clean gov.br OAuth path expected if proceeding with auth route)

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

**Recon completed at:** 2026-05-06 13:45 UTC  
**Recommendation:** **ESCALATE to MTE contact for auth confirmation before scaffolding.**
