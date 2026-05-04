import { useAdminData } from "../../hooks/useAdminData";
import { useAlerts } from "../../hooks/useAlerts";

function Skeleton() {
  return <div className="w-10 h-3 bg-[#f0f0f0] animate-pulse mx-auto" />;
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
    <div className="grid grid-cols-4 gap-4">
      {metrics.map((m) => (
        <div key={m.label} className="flex flex-col items-center">
          {isLoading && m.value === null ? (
            <Skeleton />
          ) : (
            <span className="font-mono text-[20px] font-medium tabular-nums text-[#111]">
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
