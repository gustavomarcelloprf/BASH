import type { Alert } from "../../hooks/useAlerts";

interface Props { alerts: Alert[] }

export function AlertList({ alerts }: Props) {
  if (alerts.length === 0) {
    return <p className="text-xs text-[#aaa] text-center py-4">nenhum projeto em alerta</p>;
  }

  return (
    <div className="px-4 space-y-3">
      {alerts.map((a) => {
        const pct = Math.min(a.percent * 100, 100);
        const fillClass = a.status === "critical" ? "bg-[#111]" : "bg-[#999]";
        return (
          <div key={a.project_id}>
            <div className="flex justify-between items-baseline mb-1">
              <span className="text-xs text-[#333] truncate max-w-[60%]">{a.project_name}</span>
              <span className="text-xs font-mono text-[#666]">{Math.round(a.percent * 100)}%</span>
            </div>
            <div className="h-[3px] bg-[#f0f0f0] rounded overflow-hidden">
              <div className={`h-full ${fillClass}`} style={{ width: `${pct}%` }} />
            </div>
            <p className="text-[10px] text-[#aaa] mt-0.5 font-mono">
              {a.consumed_hours}h / {a.budget_hours}h
            </p>
          </div>
        );
      })}
    </div>
  );
}
