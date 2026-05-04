import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AppHeader } from "../components/AppHeader";
import { MetricsBar } from "../components/MetricsBar";
import { ChatInput } from "../components/ChatInput";
import { AlertList } from "../components/AlertList";
import { EntryList } from "../components/EntryList";
import { useAlerts } from "../hooks/useAlerts";
import { useAuthStore } from "../stores/auth";

const CARD = "border border-[#e5e5e5] rounded-[12px] p-5 bg-white mb-4";

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[11px] font-semibold text-[#999] tracking-[0.08em] uppercase mb-3">
      {children}
    </p>
  );
}

export default function Home() {
  const { data: alerts = [] } = useAlerts();
  const [offline, setOffline] = useState(!navigator.onLine);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    const goOffline = () => setOffline(true);
    const goOnline = () => setOffline(false);
    window.addEventListener("offline", goOffline);
    window.addEventListener("online", goOnline);
    return () => {
      window.removeEventListener("offline", goOffline);
      window.removeEventListener("online", goOnline);
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#f9f9f9]">
      {offline && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            zIndex: 999,
            background: "#333",
            color: "#fff",
            textAlign: "center",
            padding: "10px 16px",
            fontSize: "13px",
          }}
        >
          sem conexão — seus dados serão enviados quando reconectar
        </div>
      )}
      <div className="mx-auto max-w-[480px] min-h-screen flex flex-col">
        <AppHeader />
        <div className="flex-1 px-4 pt-5 pb-8">

          <div className={CARD}>
            <SectionLabel>resumo do mês</SectionLabel>
            <MetricsBar />
          </div>

          <div className={CARD}>
            <SectionLabel>registrar tempo</SectionLabel>
            <ChatInput />
          </div>

          {alerts.length > 0 && (
            <div className={CARD}>
              <SectionLabel>alertas</SectionLabel>
              <AlertList alerts={alerts} />
            </div>
          )}

          <div className={CARD}>
            <SectionLabel>entradas</SectionLabel>
            <EntryList />
          </div>

          {user?.role === "admin" && (
            <div className="px-1">
              <Link
                to="/admin"
                className="text-[11px] text-[#999] hover:text-[#333] transition-colors duration-[120ms]"
              >
                Gerenciar usuários →
              </Link>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
