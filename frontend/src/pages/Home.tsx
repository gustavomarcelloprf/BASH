import { useEffect, useState } from "react";
import { MetricsBar } from "../components/MetricsBar";
import { ChatInput } from "../components/ChatInput";
import { AlertList } from "../components/AlertList";
import { EntryList } from "../components/EntryList";
import { useAlerts } from "../hooks/useAlerts";

export default function Home() {
  const { data: alerts = [] } = useAlerts();
  const [offline, setOffline] = useState(!navigator.onLine);

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
      <div
        className="mx-auto max-w-[480px] bg-white min-h-screen flex flex-col shadow-sm"
        style={{ paddingTop: offline ? "40px" : undefined }}
      >
        <MetricsBar />
        <ChatInput />
        {alerts.length > 0 && (
          <div className="py-3 border-b border-[#f0f0f0]">
            <p className="px-4 mb-2 text-[11px] uppercase tracking-widest text-[#aaa]">alertas</p>
            <AlertList alerts={alerts} />
          </div>
        )}
        <div className="flex-1 overflow-y-auto">
          <EntryList />
        </div>
      </div>
    </div>
  );
}
