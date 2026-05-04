import { useState } from "react";
import { Link } from "react-router-dom";
import { AppHeader } from "../components/AppHeader";
import { AdminMetricsBar, UserRow, ImportPanel } from "../components/Admin";
import { AlertList } from "../components/AlertList";
import { useAdminData } from "../hooks/useAdminData";
import { useAlerts } from "../hooks/useAlerts";
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";
import { api } from "../lib/api";

const CARD = "border border-[#e5e5e5] rounded-[12px] p-5 bg-white mb-4";

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[11px] font-semibold text-[#999] tracking-[0.08em] uppercase mb-3">
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
    <div className="min-h-screen bg-[#f9f9f9]">
      <div className="mx-auto max-w-[480px] min-h-screen flex flex-col">
        <AppHeader />
        <div className="px-4 pt-4 pb-8">

          <Link
            to="/"
            className="block text-[11px] text-[#999] hover:text-[#333] mb-4 transition-colors duration-[120ms]"
          >
            ← voltar
          </Link>

          {/* Métricas */}
          <div className={CARD}>
            <SectionLabel>métricas</SectionLabel>
            <AdminMetricsBar />
          </div>

          {/* Visão Geral */}
          <div className={CARD}>
            <SectionLabel>visão geral</SectionLabel>
            <div className="grid grid-cols-2 gap-3">
              <div className="border border-[#e5e5e5] rounded-lg p-3">
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
              <div className="border border-[#e5e5e5] rounded-lg p-3">
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

          {/* Usuários — sem padding lateral para as linhas irem de borda a borda */}
          <div className="border border-[#e5e5e5] rounded-[12px] bg-white mb-4 overflow-hidden" aria-live="polite">
            <div className="px-5 pt-5 pb-2">
              <SectionLabel>usuários</SectionLabel>
            </div>
            {isLoading || !users ? (
              [1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3 px-5 py-3 border-b border-[#f0f0f0]">
                  <div className="flex-1 h-3 bg-[#f0f0f0] animate-pulse" />
                </div>
              ))
            ) : (
              users.map((u) => (
                <UserRow key={u.id} user={u} currentUserId={currentUser?.id ?? -1} />
              ))
            )}
          </div>

          {/* Projetos */}
          <div className={CARD}>
            <SectionLabel>projetos em alerta</SectionLabel>
            <AlertList alerts={alerts} />
          </div>

          {/* Importar */}
          <div className={CARD}>
            <SectionLabel>importar</SectionLabel>
            <div aria-live="polite">
              <ImportPanel />
            </div>
          </div>

          {/* Relatórios */}
          <div className={CARD}>
            <SectionLabel>relatórios</SectionLabel>
            <button
              onClick={exportPdf}
              disabled={exporting}
              className={`text-[13px] px-3 py-2 border border-[#e5e5e5] rounded transition-colors duration-[120ms] ${
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
    </div>
  );
}
