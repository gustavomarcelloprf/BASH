# DASH — Login Page Overrides

> Leia primeiro este arquivo ao construir a tela de Login.
> Regras aqui **sobrepõem** `design-system/dash/MASTER.md`.
> Onde não há override, siga o Master.

---

## Contexto da Tela

- **Rota:** `/login` (pública, redireciona para `/` se já autenticado)
- **Padrão:** Formulário centralizado, sem decoração
- **Público:** Advogado fazendo login, provavelmente em mobile
- **Fluxo único:** Preencher email + senha → entrar → redirect para Home

---

## Layout

```
┌──────────────────────────────────────────────┐
│                                              │
│                                              │
│  DASH                   ← logotipo texto     │
│                                              │
│  email                  ← label             │
│  [________________]     ← input border-b    │
│                                              │
│  senha                                       │
│  [________________]                          │
│                                              │
│  [      entrar      ]   ← btn full-width     │
│                                              │
│  [mensagem de erro]     ← inline, sem cor    │
│                                              │
│                                              │
└──────────────────────────────────────────────┘
```

**Override de max-width:**
O Login usa `max-w-[360px]` (mais estreito que o padrão de 480px) — formulários de login muito largos parecem vencidos.

**Classes do container:**
```
min-h-screen bg-white flex flex-col justify-center px-8
max-w-[360px] mx-auto
```

---

## Tipografia — Override Login

| Elemento | Spec |
|----------|------|
| Logotipo "DASH" | `text-2xl font-semibold text-[#111] tracking-tight mb-10` |
| Labels dos campos | `text-[13px] font-medium text-[#333] mb-1 block` |
| Texto do input | `text-base text-[#111]` (16px — sem zoom iOS) |
| Placeholder | `text-[#999]` |
| Texto do botão | `text-[14px] font-medium text-white` |
| Mensagem de erro | `text-[13px] text-[#333] mt-3` |

---

## Inputs — Override: Border-bottom Only

Na tela de Login, inputs usam apenas `border-bottom` (não full border).
Isso reforça a estética minimalista e remete a formulários impressos.

```css
/* Override do padrão de input do Master */
border: none;
border-bottom: 1px solid #e5e5e5;
border-radius: 0;
padding: 8px 0;           /* sem padding lateral — alinha com labels */
background: transparent;
width: 100%;
font-size: 16px;
color: #111;
outline: none;
transition: border-color 200ms ease;

/* Foco */
:focus {
  border-bottom: 2px solid #111;
}
```

Classe Tailwind equivalente:
```
border-0 border-b border-[#e5e5e5] py-2 px-0 text-base text-[#111] outline-none 
focus:border-b-2 focus:border-[#111] transition-colors duration-200 bg-transparent w-full
```

---

## Botão Submit — Override Login

Botão full-width, sem border-radius, preto sólido.

```
w-full bg-[#111] text-white py-3 text-sm font-medium mt-8
cursor-pointer hover:bg-[#333] transition-colors duration-200
border-radius: 0    ← override explícito (Master permite até 4px)
```

**Estados:**

| Estado | Aparência |
|--------|-----------|
| Default | `bg-[#111] text-white` |
| Hover | `bg-[#333]` — 200ms |
| Loading | `opacity-60 pointer-events-none` + texto "entrando..." |
| Disabled | `opacity-40 cursor-not-allowed` |

---

## Mensagem de Erro — Override Login

Sem caixa de erro, sem bordas de erro, sem cor de alerta.
O erro aparece como texto simples abaixo do botão.

```
text-[13px] text-[#333] mt-3
aria-live="polite"
```

- Texto exemplo: `"email ou senha incorretos"`
- Nunca use "senha inválida" ou "usuário não encontrado" (informação de segurança)
- Sem ícone de erro

---

## Atributos de Formulário

```html
<form autocomplete="on">
  <label for="email">email</label>
  <input
    id="email"
    type="email"
    autocomplete="email"
    inputMode="email"
    autoFocus
    required
  />

  <label for="password">senha</label>
  <input
    id="password"
    type="password"
    autocomplete="current-password"
    required
  />

  <button type="submit">entrar</button>
</form>
```

**Regras:**
- `autoFocus` no campo email — usuário não precisa tocar
- `autocomplete` habilitado — gerenciadores de senha funcionam
- `inputMode="email"` no campo email — teclado correto no mobile
- `type="password"` — mascaramento nativo do browser/OS
- Labels em minúsculas (estilo DASH) — `"email"`, `"senha"`

---

## O que NÃO incluir no Login

| Elemento | Motivo |
|----------|--------|
| Link "esqueci a senha" | Fora de escopo do MVP |
| Link "criar conta" | Contas são criadas via `scripts/create_user.py` |
| Logo com ícone/imagem | DASH usa apenas tipografia |
| Ilustração ou fundo decorativo | Contexto profissional austero |
| Checkbox "lembrar de mim" | Session storage por decisão técnica |
| Toast de erro | Erro de login é inline, não toast |
| Divisor "ou continue com" | Sem OAuth no MVP |
| Borda ao redor do formulário | Sem card wrapper — direto na página |

---

## Acessibilidade — Overrides Login

| Regra | Implementação |
|-------|--------------|
| Focus inicial | `autoFocus` no input email |
| Erro anunciado | `aria-live="polite"` na zona de erro |
| Botão durante loading | `aria-disabled="true"` + `aria-busy="true"` |
| Labels visíveis | `<label>` explícito, nunca só placeholder |
| Enter submete | `type="submit"` nativo — Enter funciona |

---

## Checklist de Entrega — Login

- [ ] `max-w-[360px]` (não 480px)
- [ ] Inputs com `border-bottom` apenas (sem full border)
- [ ] `font-size: 16px` nos inputs (sem zoom iOS)
- [ ] `autoFocus` no campo email
- [ ] `autocomplete` configurado em ambos os campos
- [ ] Botão desabilitado durante request com `aria-busy="true"`
- [ ] Erro de credenciais em texto inline, sem cor de alerta
- [ ] `aria-live="polite"` na zona de erro
- [ ] Redirect automático para `/` se já autenticado
- [ ] Testado em 375px (iPhone SE) — sem overflow
