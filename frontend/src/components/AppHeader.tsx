import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/auth";

export function AppHeader() {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-[#e5e5e5] flex items-center justify-between px-6 py-4">
      <span className="font-mono font-bold text-[18px] text-[#111]">DASH</span>
      <button
        onClick={() => { logout(); navigate("/login"); }}
        className="text-[13px] text-[#999] hover:text-[#111] transition-colors duration-[120ms] bg-transparent border-none cursor-pointer p-0"
      >
        sair
      </button>
    </header>
  );
}
