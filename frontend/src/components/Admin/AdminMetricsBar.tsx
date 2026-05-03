import { useAdminData } from "../../hooks/useAdminData";
import { useAlerts } from "../../hooks/useAlerts";

function Skeleton() {
  return <div className="w-10 h-3 bg-[#f0f0f0] animate-pulse" />;
}

export function AdminMetricsBar() {
  const { users, roi, isLoading } = useAdminData();
  const { data: alerts = [] } = useAlerts();

  const totalHours = users
    ? users.reduce((s, u) => s + u.hours_this_month, 0).toFixed(1) + "h"
    : null;
  const activeUsers = users ? String(users.filter((u) => u.is_active).length) : null;
  const alertCount = String(alerts.length);
  const roiHours = roi ? roi.total_hours_saved.toFixed(1) + "h" : null;

  const metrics = [
    { value: totalHours, label: "equipe" },
    { value: activeUsers, label: "ativos" },
    { value: alertCount, label: "alertas" },
    { value: roiHours, label: "salvas" },
  ];

  return (
    <div className="sticky top-0 z-10 bg-white border-b border-[#e5e5e5] h-16 flex items-center justify-between px-3">
      {metrics.map((m) => (
        <div key={m.label} className="flex flex-col items-center">
          {isLoading && m.value === null ? (
            <Skeleton />
          ) : (
            <span className="font-mono text-[18px] font-medium tabular-nums text-[#111]">
              {m.value ?? "—"}
            </span>
          )}
          <span className="text-[9px] uppercase tracking-widest text-[#aaa] mt-0.5">
            {m.label}
          </span>
        </div>
      ))}
    </div>
  );
}
