import { useState, type FormEvent } from "react";
import { useAuth } from "../hooks/useAuth";

type Mode = "login" | "register";

export default function Login() {
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const { login, register } = useAuth();

  const submitLogin = (e: FormEvent) => {
    e.preventDefault();
    login.mutate({ email, password });
  };

  const submitRegister = (e: FormEvent) => {
    e.preventDefault();
    if (password !== confirm) return;
    register.mutate(
      { name, email, password },
      {
        onSuccess: () => {
          setSuccessMsg("Cadastro realizado! Aguarde aprovação do administrador.");
          setTimeout(() => {
            setSuccessMsg("");
            setMode("login");
            setName("");
            setPassword("");
            setConfirm("");
          }, 3000);
        },
      }
    );
  };

  return (
    <div className="min-h-screen bg-[#f9f9f9] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="font-mono font-bold text-2xl text-[#111] mb-8">DASH</h1>

        {successMsg ? (
          <p className="text-sm text-[#333] bg-[#f0f0f0] px-4 py-3 rounded">{successMsg}</p>
        ) : mode === "login" ? (
          <>
            <form onSubmit={submitLogin} className="space-y-3">
              <input
                type="email"
                placeholder="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-[#e5e5e5] rounded px-3 py-2 text-sm bg-white outline-none focus:border-[#999]"
                required
              />
              <input
                type="password"
                placeholder="senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-[#e5e5e5] rounded px-3 py-2 text-sm bg-white outline-none focus:border-[#999]"
                required
              />
              {login.isError && (
                <p className="text-xs text-[#666]">
                  {(login.error as any)?.response?.data?.detail ?? "email ou senha incorretos"}
                </p>
              )}
              <button
                type="submit"
                disabled={login.isPending}
                className="w-full bg-[#111] text-white text-sm rounded py-2 font-mono hover:bg-[#333] disabled:opacity-50"
              >
                {login.isPending ? "entrando…" : "entrar"}
              </button>
            </form>
            <p className="mt-4 text-xs text-[#999] text-center">
              Não tem conta?{" "}
              <button
                onClick={() => { setMode("register"); login.reset(); }}
                className="text-[#555] underline hover:text-[#111]"
              >
                Criar conta
              </button>
            </p>
          </>
        ) : (
          <>
            <form onSubmit={submitRegister} className="space-y-3">
              <input
                type="text"
                placeholder="nome completo"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-[#e5e5e5] rounded px-3 py-2 text-sm bg-white outline-none focus:border-[#999]"
                required
              />
              <input
                type="email"
                placeholder="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-[#e5e5e5] rounded px-3 py-2 text-sm bg-white outline-none focus:border-[#999]"
                required
              />
              <input
                type="password"
                placeholder="senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-[#e5e5e5] rounded px-3 py-2 text-sm bg-white outline-none focus:border-[#999]"
                required
                minLength={8}
              />
              <input
                type="password"
                placeholder="confirmar senha"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="w-full border border-[#e5e5e5] rounded px-3 py-2 text-sm bg-white outline-none focus:border-[#999]"
                required
              />
              {confirm && password !== confirm && (
                <p className="text-xs text-[#666]">senhas não conferem</p>
              )}
              {register.isError && (
                <p className="text-xs text-[#666]">
                  {(register.error as any)?.response?.data?.detail ?? "erro ao cadastrar"}
                </p>
              )}
              <button
                type="submit"
                disabled={register.isPending || password !== confirm}
                className="w-full bg-[#111] text-white text-sm rounded py-2 font-mono hover:bg-[#333] disabled:opacity-50"
              >
                {register.isPending ? "cadastrando…" : "criar conta"}
              </button>
            </form>
            <p className="mt-4 text-xs text-[#999] text-center">
              Já tem conta?{" "}
              <button
                onClick={() => { setMode("login"); register.reset(); }}
                className="text-[#555] underline hover:text-[#111]"
              >
                Entrar
              </button>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
