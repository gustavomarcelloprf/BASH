# DASH — Home Page Overrides

> Leia primeiro este arquivo ao construir qualquer componente da tela Home.
> Regras aqui **sobrepõem** `design-system/dash/MASTER.md`.
> Onde não há override, siga o Master.

---

## Contexto da Tela

- **Rota:** `/` (requer autenticação)
- **Padrão:** Single Page App — scroll vertical único
- **Público:** Advogado logado, uso diário, input rápido
- **Fluxo primário:** Digitar entrada de tempo → ver preview → submeter → lista atualiza

---

## Layout Geral

```
┌──────────────────────────────────────────────┐
│  MetricsBar (sticky, 64px, z-10)            │
├──────────────────────────────────────────────┤
│  ChatInput (parte do fluxo, não sticky)      │
│    └─ LivePreview inline                     │
├──────────────────────────────────────────────┤
│  AlertList (condicional — só se alerts > 0)  │
├──────────────────────────────────────────────┤
│  EntryList (flex-1, overflow-y-auto)         │
└──────────────────────────────────────────────┘
```

**Classes do container raiz:**
```
min-h-screen bg-[#f9f9f9]
```

**Classes do card central:**
```
mx-auto max-w-[480px] bg-white min-h-screen flex flex-col shadow-sm
```

---

## Z-index Stack

| Camada | z-index | Elemento |
|--------|---------|----------|
| 0 | `z-0` | EntryList, AlertList |
| 10 | `z-10` | MetricsBar (sticky) |
| 999 | `z-[999]` | Banner offline (fixed) |
| 1000 | `z-[1000]` | Toast (fixed) |

---

## Banner Offline

Exibido quando `navigator.onLine === false`. Desaparece automaticamente ao reconectar.

```
position: fixed; top: 0; left: 0; right: 0; z-index: 999
background: #333; color: #fff
font-size: 13px; padding: 10px 16px; text-align: center
texto: "sem conexão — seus dados serão enviados quando reconectar"
```

- `role="alert"` + `aria-live="assertive"` (estado crítico)
- Quando offline: adicionar `paddingTop: 40px` ao card para não cobrir conteúdo
- Sem botão de fechar — some automaticamente ao reconectar
- Sem transição de aparecimento (informação urgente deve ser imediata)

---

## ChatInput — Overrides Home

- Posição: imediatamente abaixo do MetricsBar
- `border-t border-[#e5e5e5]` (separa do MetricsBar)
- Background: `bg-white`
- Padding: `px-4 pt-3 pb-2`
- Placeholder: `"quanto tempo você trabalhou hoje?"`
- Focus automático ao montar a página
- Cresce verticalmente (auto-expand via scrollHeight), máximo 3 linhas
- Após submit: limpa e retorna a 1 linha em 150ms

---

## AlertList — Seção Condicional

Só renderiza quando `alerts.length > 0`. Sem transição de entrada (evita CLS).

**Wrapper:**
```
py-3 border-b border-[#f0f0f0]
```

**Label:**
```
px-4 mb-2 text-[10px] uppercase tracking-widest text-[#aaa]
texto: "alertas"
```

- Máximo 3 alertas visíveis; se > 3: `max-h-[180px] overflow-y-auto`

---

## EntryList — Posição e Scroll

- `flex-1 overflow-y-auto` — ocupa o espaço restante
- Label: `"entradas deste mês"` — `text-[10px] uppercase tracking-widest text-[#aaa] px-4 py-3`
- **Empty state:** `flex-1 flex flex-col items-center justify-center text-[#999] text-sm text-center px-8`
  - Texto: `"nenhum registro este mês\ndigite sua primeira entrada acima"`

---

## Toast — Posição Home

```css
bottom: calc(24px + env(safe-area-inset-bottom, 0px));
left: 50%;
transform: translateX(-50%);
z-index: 1000;
```

---

## Fluxo de Interação

```
1. Montar página → MetricsBar skeleton → dados → focus no ChatInput
2. Digitar → useParser debounce 300ms → LivePreview atualiza
3. Enter → createEntry → limpa input → EntryList recarrega
   Erro → Toast "erro ao salvar entrada" (4s)
4. × em linha → optimistic delete
   Erro de rede → rollback + Toast "erro ao remover entrada"
5. Offline → banner aparece → some ao reconectar
```

---

## Checklist de Entrega — Home

- [ ] MetricsBar sticky com `z-10` funcional sobre scroll
- [ ] Banner offline com `role="alert"` + `aria-live="assertive"`
- [ ] ChatInput com focus automático na montagem
- [ ] LivePreview com `aria-live="polite"`
- [ ] AlertList só renderiza se `alerts.length > 0`
- [ ] EntryList com estado vazio e mensagem útil
- [ ] Toast com `role="status"` + `aria-live="polite"`
- [ ] Scroll da EntryList não conflita com scroll da página
- [ ] Testado em 375px sem overflow horizontal
- [ ] `prefers-reduced-motion` aplicado em LivePreview e Toast
