import { useDashboard } from "../../hooks/useDashboard";

function Skeleton() {
  return <span className="inline-block w-12 h-3 bg-[#e5e5e5] rounded animate-pulse" />;
}

export function MetricsBar() {
  const { data, isLoading } = useDashboard();

  return (
    <div className="sticky top-0 z-10 bg-white border-b border-[#e5e5e5] h-16 flex items-center px-4 gap-6">
      <span className="text-xs text-[#666]">
        {isLoading ? <Skeleton /> : <span className="font-mono font-bold text-[#111]">{data?.total_hours ?? 0}h</span>}
        {" · mês"}
      </span>
      <span className="text-xs text-[#666]">
        {isLoading ? <Skeleton /> : <span className="font-mono font-bold text-[#111]">{data?.active_projects ?? 0}</span>}
        {" proj"}
      </span>
      <span className="text-xs text-[#666]">
        {isLoading ? <Skeleton /> : <span className="font-mono font-bold text-[#111]">{data?.roi_hours_saved ?? 0}h</span>}
        {" salvas"}
      </span>
    </div>
  );
}
