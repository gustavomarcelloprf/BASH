# DASH — Design System Master

> **HIERARQUIA:** Ao construir uma página, leia primeiro `design-system/dash/pages/[página].md`.
> Se o arquivo existir, suas regras **sobrepõem** este Master.
> Se não existir, siga exclusivamente as regras abaixo.

---

**Projeto:** DASH — Rastreio de horas em escritório jurídico
**Versão:** 1.0.0
**Stack:** React 18 · TypeScript · Tailwind CSS 3 · Mobile-first 480px

---

## Alternativas Consideradas e Rejeitadas pelo Motor

O motor sugeriu em diferentes sessões:
- **Sessão 1 (home/login):** Motion-Driven, Plus Jakarta Sans, paleta dark tech `#0F172A` + verde `#22C55E`
- **Sessão 2 (admin):** Data-Dense Dashboard, Fira Code/Fira Sans, paleta vermelha `#DC2626`

**Ambas rejeitadas:** Paletas cromáticas (verde, vermelho) são inadequadas para ambiente jurídico. Advocacia exige neutralidade visual. Motion-Driven gera carga cognitiva em uso diário intenso. Tipografias alternativas foram preteridas pois Inter+JetBrains Mono já estão implementadas.

---

## 1. Tokens de Cor

Paleta restrita: **apenas preto, branco e escala de cinzas neutros**.

| Token | Hex | Tailwind | Uso |
|-------|-----|----------|-----|
| `--c-black` | `#111111` | `text-[#111]` | Texto primário, bordas ativas |
| `--c-ink` | `#333333` | `text-[#333]` | Rótulos, títulos secundários |
| `--c-mid` | `#666666` | `text-[#666]` | Texto auxiliar |
| `--c-muted` | `#999999` | `text-[#999]` | Placeholder, metadados, ações secundárias |
| `--c-subtle` | `#aaaaaa` | `text-[#aaa]` | Labels uppercase de seção |
| `--c-border` | `#e5e5e5` | `border-[#e5e5e5]` | Divisores, bordas repouso |
| `--c-surface-2` | `#f0f0f0` | `bg-[#f0f0f0]` | Skeleton, hover de linhas |
| `--c-surface-1` | `#f9f9f9` | `bg-[#f9f9f9]` | Fundo externo ao card |
| `--c-white` | `#ffffff` | `bg-white` | Card principal, superfície primária |

**Regras absolutas:**
- Proibido qualquer cor fora desta tabela
- Proibido gradientes, sombras coloridas, `backdrop-filter`
- O único acento é borda `2px solid #111` para estado ativo/foco
- Sem vermelho, verde, amarelo ou azul em qualquer elemento funcional

### Contraste WCAG AA

| Par | Ratio | Status |
|-----|-------|--------|
| `#111` sobre `#fff` | 18.1:1 | ✅ AAA |
| `#333` sobre `#fff` | 10.7:1 | ✅ AAA |
| `#666` sobre `#fff` | 5.7:1 | ✅ AA |
| `#999` sobre `#fff` | 2.8:1 | ⚠ Só decorativo |
| `#aaa` sobre `#fff` | 2.3:1 | ⚠ Só labels uppercase |

---

## 2. Tipografia

```css
font-family: 'Inter', system-ui, sans-serif;       /* UI */
font-family: 'JetBrains Mono', monospace;          /* Números */
```

| Role | Size | Weight | Font | Tailwind |
|------|------|--------|------|---------|
| `metric` | 22–28px | 500 | Mono | `font-mono text-[22px] font-medium tabular-nums` |
| `title` | 18px | 600 | Inter | `text-lg font-semibold` |
| `label` | 13px | 500 | Inter | `text-[13px] font-medium` |
| `body` | 14px | 400 | Inter | `text-sm` |
| `caption` | 11px | 400 | Inter | `text-[11px]` |
| `tag` | 10px | 400 | Inter uppercase | `text-[10px] uppercase tracking-widest` |
| `input` | 16px | 400 | Inter | `text-base` (evita zoom iOS) |
| `entry-hours` | 15px | 500 | Mono | `font-mono text-[15px] font-medium tabular-nums` |

**Regras:** `tabular-nums` obrigatório em números. Peso máximo: `font-semibold` (600).

---

## 3. Espaçamento — Grid de 8px

| px | Tailwind |
|----|---------|
| 4 | `p-1 / gap-1` |
| 8 | `p-2 / gap-2` |
| 12 | `p-3 / gap-3` |
| 16 | `p-4 / gap-4` |
| 24 | `p-6 / gap-6` |
| 32 | `p-8` |
| 64 | `h-16` (MetricsBar) |

---

## 4. Bordas e Geometria

| Propriedade | Valor |
|-------------|-------|
| `border-radius` padrão | `0px` |
| `border-radius` máximo | `4px` |
| Borda repouso | `1px solid #e5e5e5` |
| Borda ativa/foco | `2px solid #111` |
| Sombras | Proibidas (exceto `0 1px 3px rgba(0,0,0,0.06)` no card principal) |

---

## 5. Motion System

| Nome | Duração | Uso |
|------|---------|-----|
| `micro` | 120ms | Hover cor/opacidade |
| `fast` | 200ms | Foco input, estado botão |
| `standard` | 250ms | Toast, banner |
| `slow` | 350ms | Progress bar, LivePreview |

**Easings:** `cubic-bezier(0.0, 0.0, 0.2, 1)` entradas · `cubic-bezier(0.4, 0.0, 1, 1)` saídas.
**Animar apenas:** `opacity`, `transform`, `border-color`, `background-color`.
**`prefers-reduced-motion`:** todas as durações → 0ms.

---

## 6. Z-index Stack Global

| z-index | Elemento |
|---------|----------|
| 0 | Conteúdo normal |
| 10 | MetricsBar sticky |
| 999 | Banner offline |
| 1000 | Toast |

---

## 7. Componentes Base

### MetricsBar
`sticky top-0 z-10 bg-white border-b border-[#e5e5e5] h-16`
Valores: `font-mono tabular-nums text-[#111]` · Labels: `text-[10px] uppercase tracking-widest text-[#aaa]`

### Toast
`fixed bottom-6 left-1/2 -translate-x-1/2 z-[1000] bg-white border border-[#333] px-5 py-3 text-[14px]`
Auto-dismiss 4s · `aria-live="polite"` · `role="status"` · Slide `translateY(120%→0)` 250ms

### EntryList linha
`flex items-center gap-3 px-4 py-3 hover:bg-[#f9f9f9] transition-colors duration-[120ms] border-b border-[#f0f0f0]`

### Input padrão
`border-b border-[#e5e5e5] py-2 text-base outline-none focus:border-[#111] transition-colors duration-200 bg-transparent`

### Botão primário
`bg-[#111] text-white py-3 text-sm font-medium cursor-pointer hover:bg-[#333] transition-colors duration-200`

---

## 8. Anti-patterns — Contexto Jurídico

| Anti-pattern | Motivo |
|--------------|--------|
| Cores de status (vermelho/verde/amarelo) | Geram ansiedade em ambiente de alta pressão |
| `border-radius > 4px` | Estética consumer — DASH é ferramenta profissional |
| Gradientes / glassmorphism | Decoração incompatível com seriedade jurídica |
| Animações decorativas | Aumentam carga cognitiva em uso diário |
| Modais / dialogs / overlays | Interrompem fluxo de trabalho |
| Emojis como ícones | Inconsistentes entre plataformas |
| Placeholder como único label | Viola WCAG 1.3.5 |

---

## 9. Checklist Pré-entrega

- [ ] Cores somente da tabela de tokens (seção 1)
- [ ] `border-radius` ≤ 4px
- [ ] `tabular-nums` em valores numéricos
- [ ] `cursor-pointer` em elementos clicáveis
- [ ] `font-size >= 16px` em inputs
- [ ] `aria-label` em botões sem texto visível
- [ ] `aria-live` em zonas dinâmicas
- [ ] `prefers-reduced-motion` respeitado
- [ ] Testado em 375px sem overflow horizontal
- [ ] Alvos de toque mínimo 44×44px
