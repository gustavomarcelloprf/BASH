import type { ParseResult } from "../../types";

interface Props { result: ParseResult | undefined; loading: boolean }

export function LivePreview({ result, loading }: Props) {
  if (loading) return <p className="text-xs text-[#999] mt-1">analisando…</p>;
  if (!result || result.hours === null) return null;

  const today = new Date().toISOString().slice(0, 10);
  const dateLabel = result.date === today ? "hoje" : result.date;
  const parts = [
    `${result.hours}h`,
    result.activity ?? result.project ?? "—",
    dateLabel,
  ];

  return (
    <p className="text-xs text-[#333] mt-1 font-mono">
      {parts.join(" · ")}
      {result.confidence < 0.7 && (
        <span className="ml-2 text-[#999]">(baixa confiança)</span>
      )}
    </p>
  );
}
