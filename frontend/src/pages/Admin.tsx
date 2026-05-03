import { useState } from "react";
import { Link } from "react-router-dom";
import { AdminMetricsBar, UserRow, ImportPanel } from "../components/Admin";
import { AlertList } from "../components/AlertList";
import { useAdminData } from "../hooks/useAdminData";
import { useAlerts } from "../hooks/useAlerts";
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";
import { api } from "../lib/api";

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="px-4 pt-4 pb-2 text-[10px] uppercase tracking-widest text-[#aaa]">
      {children}
    </p>
  );
}

export default function Admin() {
  const [exporting, setExporting] = useState(false);
  const toast = useToastStore();
  const { users, roi: _roi, isLoading } = useAdminData();

  const exportPdf = async () => {
    setExporting(true);
    try {
      const resp = await api.post("/api/reports/generate", { period: "month" }, { responseType: "blob" });
      const url = URL.createObjectURL(resp.data as Blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `relatorio_${new Date().toISOString().slice(0, 7)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.show("erro ao gerar PDF", "error");
    } finally {
      setExporting(false);
    }
  };
  const { data: alerts = [] } = useAlerts();
  const currentUser = useAuthStore((s) => s.user);

  const topUser = users
    ? [...users].sort((a, b) => b.hours_this_month - a.hours_this_month)[0] ?? null
    : null;
  const topAlert = [...alerts].sort((a, b) => b.percent - a.percent)[0] ?? null;

  return (
    <div className="mx-auto max-w-[480px] bg-white min-h-screen">
      <Link
        to="/"
        className="block px-4 py-2 text-[11px] text-[#999] hover:text-[#333]"
      >
        ← voltar
      </Link>

      <AdminMetricsBar />

      <div className="border-t border-[#f0f0f0]">
        <SectionLabel>visão geral</SectionLabel>
        <div className="grid grid-cols-2 gap-3 px-4 py-3">
          <div className="border border-[#e5e5e5] p-3">
            <p className="text-[10px] uppercase tracking-widest text-[#aaa] mb-1">top usuário</p>
            {isLoading || !topUser ? (
              <div className="w-20 h-3 bg-[#f0f0f0] animate-pulse" />
            ) : (
              <>
                <p className="text-[13px] font-medium text-[#333]">{topUser.name}</p>
                <p className="font-mono text-[13px] tabular-nums text-[#111]">
                  {topUser.hours_this_month.toFixed(1)}h
                </p>
              </>
            )}
          </div>
          <div className="border border-[#e5e5e5] p-3">
            <p className="text-[10px] uppercase tracking-widest text-[#aaa] mb-1">top projeto</p>
            {!topAlert ? (
              <p className="text-[13px] text-[#999]">—</p>
            ) : (
              <>
                <p className="text-[13px] font-medium text-[#333] truncate">
                  {topAlert.project_name}
                </p>
                <p className="font-mono text-[13px] tabular-nums text-[#111]">
                  {Math.round(topAlert.percent * 100)}%
                </p>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="border-t border-[#f0f0f0]" aria-live="polite">
        <SectionLabel>usuários</SectionLabel>
        {isLoading || !users ? (
          <div>
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="flex items-center gap-3 px-4 py-3 border-b border-[#f0f0f0]"
              >
                <div className="flex-1 h-3 bg-[#f0f0f0] animate-pulse" />
              </div>
            ))}
          </div>
        ) : (
          users.map((u) => (
            <UserRow key={u.id} user={u} currentUserId={currentUser?.id ?? -1} />
          ))
        )}
      </div>

      <div className="border-t border-[#f0f0f0]">
        <SectionLabel>projetos</SectionLabel>
        <div className="py-3">
          <AlertList alerts={alerts} />
        </div>
      </div>

      <div className="border-t border-[#f0f0f0]">
        <SectionLabel>importar</SectionLabel>
        <div className="px-4 pb-4" aria-live="polite">
          <ImportPanel />
        </div>
      </div>

      <div className="border-t border-[#f0f0f0]">
        <SectionLabel>relatórios</SectionLabel>
        <div className="px-4 pb-4">
          <button
            onClick={exportPdf}
            disabled={exporting}
            className={`text-[13px] px-3 py-2 border border-[#e5e5e5] transition-colors duration-[120ms] ${
              exporting
                ? "text-[#aaa] pointer-events-none"
                : "text-[#333] hover:border-[#111] hover:text-[#111] cursor-pointer"
            }`}
          >
            {exporting ? "gerando..." : "exportar PDF"}
          </button>
          <p className="text-[11px] text-[#aaa] mt-2">relatório do mês atual · todas as entradas</p>
        </div>
      </div>
    </div>
  );
}
