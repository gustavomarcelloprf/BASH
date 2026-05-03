# DASH — Admin Page Overrides

> Leia primeiro este arquivo ao construir a página /admin.
> Regras aqui **sobrepõem** `design-system/dash/MASTER.md`.
> Onde não há override, siga o Master.

---

## Sugestão do Motor — Avaliada e Parcialmente Rejeitada

O motor sugeriu para "legal SaaS admin dashboard team management productivity":
- **Estilo aceito:** Data-Dense Dashboard — ✅ compatível com a natureza da página admin (tabelas, métricas, dados da equipe)
- **Paleta rejeitada:** `#DC2626` (vermelho) — ❌ incompatível com MASTER.md. Admin usa a mesma paleta neutra.
- **Tipografia rejeitada:** Fira Code/Fira Sans — ❌ projeto já usa Inter+JetBrains Mono.
- **Efeitos aceitos:** row highlighting on hover, data loading skeletons — ✅ já no MASTER.md.
- **Anti-patterns aceitos:** "Ornate design" e "No filtering" — ✅ relevantes para esta página.

---

## Contexto

- **Rota:** `/admin` (protegida — só `role=admin`)
- **Redirecionamento:** member → `/` · não autenticado → `/login`
- **Padrão:** Extensão da Home — mesma estrutura, mais seções
- **Fluxo:** Admin vê dados de toda equipe, gerencia usuários, importa dados

---

## Layout Geral

```
┌──────────────────────────────────────────────┐
│  AdminMetricsBar (sticky, 64px, z-10)       │  ← 4 métricas
├──────────────────────────────────────────────┤
│  seção "visão geral"                         │  ← métricas equipe
├──────────────────────────────────────────────┤
│  seção "usuários"                            │  ← UserRow lista
├──────────────────────────────────────────────┤
│  seção "projetos"                            │  ← AlertList reutilizado
├──────────────────────────────────────────────┤
│  seção "importar"                            │  ← ImportPanel
└──────────────────────────────────────────────┘
```

**Container:** `mx-auto max-w-[480px] bg-white min-h-screen flex flex-col`
**Label de seção padrão:** `px-4 pt-4 pb-2 text-[10px] uppercase tracking-widest text-[#aaa]`
**Divisor entre seções:** `border-t border-[#f0f0f0]`

---

## Componente: AdminMetricsBar

Mesma base do MetricsBar — adapta para 4 métricas quando `role=admin`.

```
┌──────────────────────────────────────────────────────────┐
│  142.5h   ·   8 usuários   ·   3 alertas   ·   4.2h ROI │
│  equipe       ativos          budget           salvas    │
└──────────────────────────────────────────────────────────┘
```

**Tokens:**
- Container: `sticky top-0 z-10 bg-white border-b border-[#e5e5e5] h-16 flex items-center`
- Layout 4 métricas: `justify-between px-3` (reduz padding para caber 4)
- Cada métrica: `flex flex-col items-center`
- Valor: `font-mono text-[18px] font-medium tabular-nums text-[#111]` (reduz de 22px para 18px)
- Label: `text-[9px] uppercase tracking-widest text-[#aaa] mt-0.5`

**Estados:**
- Loading: skeleton `w-10 h-3 bg-[#f0f0f0] animate-pulse`
- Dados: valores com 1 decimal para horas, inteiros para contagens

**Regras:**
- Valor de ROI: horas (não R$) — consistente com MetricsBar da Home
- "alertas" conta projetos com `percent >= 0.8`
- Sem divisores verticais entre métricas

---

## Componente: UserRow

Linha na seção "usuários". Uma linha por usuário da equipe.

```
┌────────────────────────────────────────────────────────────┐
│  Ana Silva        14.5h  [admin]  promover · desativar    │  ← ativo
│  João Dev          8.0h  [member] promover · desativar    │
│  Maria Costa       0.0h  [member] promover · desativar    │
├────────────────────────────────────────────────────────────┤
│  ̶C̶a̶r̶l̶o̶s̶ ̶I̶n̶a̶t̶i̶v̶o̶    —h   [member] ativar               │  ← desativado
└────────────────────────────────────────────────────────────┘
```

**Tokens:**
- Linha: `flex items-center gap-3 px-4 py-3 border-b border-[#f0f0f0]`
  - Hover: `hover:bg-[#f9f9f9] transition-colors duration-[120ms]`
- Nome: `flex-1 text-[13px] font-medium text-[#333] truncate`
- Horas: `font-mono text-[13px] tabular-nums text-[#666] w-10 text-right shrink-0`
- Role badge:
  - `admin`: `text-[9px] uppercase tracking-wider border border-[#111] px-1.5 py-0.5 text-[#111]`
  - `member`: `text-[9px] uppercase tracking-wider border border-[#e5e5e5] px-1.5 py-0.5 text-[#999]`

**Ações (inline, texto puro):**
- Container ações: `flex items-center gap-3 shrink-0 text-[11px]`
- [promover admin] / [rebaixar member]: `text-[#666] hover:text-[#111] cursor-pointer transition-colors duration-[120ms]`
- [desativar] / [ativar]: `text-[#999] hover:text-[#333] cursor-pointer transition-colors duration-[120ms]`

**Confirmação inline de desativar:**
```
[desativar]  →  confirmar? [sim] [não]
```
- Aparece na mesma linha, substituindo o texto "desativar"
- `[sim]`: `text-[#333] cursor-pointer`
- `[não]`: `text-[#999] cursor-pointer`
- Sem modal, sem alert(), sem dialog

**Estados:**
- Usuário desativado: `opacity-50` na linha + `line-through` no nome
- Ação em andamento: texto da ação → `text-[#aaa] pointer-events-none`
- Admin não pode desativar a si mesmo: ação oculta na própria linha

**Regras:**
- Ações de promoção: toggle — se é admin mostra "rebaixar", se é member mostra "promover"
- Admin não pode se auto-rebaixar nem se desativar (back-end também bloqueia)
- Feedback de ação: Toast 4s via store existente

---

## Componente: ImportPanel

Upload de .xlsx com drag-and-drop e feedback inline.

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  (idle)    arraste um .xlsx aqui ou clique para selecionar │
│            texto centralizado, área pontilhada             │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  (dragover) borda solid #111, fundo #f9f9f9               │
├────────────────────────────────────────────────────────────┤
│  (uploading)                                               │
│  importando...                                             │
│  ████████████░░░░░░░░░░░░░░░  (progress bar 3px)          │
├────────────────────────────────────────────────────────────┤
│  (done)                                                    │
│  127 importadas · 3 ignoradas · 12 duplicatas              │
└────────────────────────────────────────────────────────────┘
```

**Tokens:**
- Área idle: `border border-dashed border-[#e5e5e5] px-4 py-8 text-center cursor-pointer`
  - Texto: `text-[13px] text-[#999]`
- Área dragover: `border border-solid border-[#111] bg-[#f9f9f9]`
- Progress track: `h-[3px] bg-[#f0f0f0] mt-4 w-full`
- Progress fill: `h-[3px] bg-[#333] transition-[width] duration-[350ms]` (sem bounce)
- Resumo done: `text-[13px] text-[#333] py-3` com separador `·` em `text-[#aaa]`

**Estados:**
- idle: área pontilhada com instrução
- dragover: borda sólida `#111` (200ms transition)
- uploading: barra de progresso simulada (0→90% durante upload, 100% ao completar)
- done: resumo de resultados inline
- error: texto de erro em `text-[#333]` inline, sem vermelho

**Regras:**
- `input[type=file]` oculto, acionado pelo click na área
- `accept=".xlsx"` no input
- Sem modal de confirmação antes do upload
- Erro de formato: texto inline "apenas arquivos .xlsx são aceitos"
- `aria-label="área de upload de arquivo"` no container clicável

---

## Seção "visão geral" — Override

Exibe resumo numérico da equipe no mês atual. Não duplica o AdminMetricsBar.

```
┌──────────────────┬──────────────────┐
│  top usuário:    │  top projeto:    │
│  Ana Silva 14h   │  Caso Silva 80%  │
└──────────────────┴──────────────────┘
```

- Layout: `grid grid-cols-2 gap-3 px-4 py-3`
- Card: `border border-[#e5e5e5] p-3`
- Label: `text-[10px] uppercase tracking-widest text-[#aaa] mb-1`
- Valor: `text-[13px] font-medium text-[#333]`
- Sub-valor: `font-mono text-[13px] tabular-nums text-[#111]`

---

## Navegação Admin ↔ Home

- Link "← voltar" no topo da página admin (acima do AdminMetricsBar)
- `text-[11px] text-[#999] hover:text-[#333] px-4 py-2 cursor-pointer`
- Sem ícone de seta — texto puro "← voltar"

---

## Checklist de Entrega — Admin

- [ ] `ProtectedRoute role="admin"` redireciona member para `/`
- [ ] AdminMetricsBar com 4 métricas em 18px mono
- [ ] UserRow com confirmação inline (sem modal)
- [ ] Admin não pode auto-rebaixar nem auto-desativar
- [ ] ImportPanel com 4 estados (idle/dragover/uploading/done)
- [ ] Barra de progresso sem bounce (`cubic-bezier` linear para upload)
- [ ] Toast feedback em todas as ações de usuário
- [ ] `aria-live="polite"` em zonas dinâmicas (resumo import, lista usuários)
- [ ] Testado em 375px sem overflow horizontal
- [ ] `npm run build` sem erros TS
