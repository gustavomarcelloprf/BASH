import { useState, type FormEvent } from "react";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();

  const submit = (e: FormEvent) => {
    e.preventDefault();
    login.mutate({ email, password });
  };

  return (
    <div className="min-h-screen bg-[#f9f9f9] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="font-mono font-bold text-2xl text-[#111] mb-8">DASH</h1>
        <form onSubmit={submit} className="space-y-3">
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
            <p className="text-xs text-[#666]">email ou senha incorretos</p>
          )}
          <button
            type="submit"
            disabled={login.isPending}
            className="w-full bg-[#111] text-white text-sm rounded py-2 font-mono hover:bg-[#333] disabled:opacity-50"
          >
            {login.isPending ? "entrando…" : "entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
