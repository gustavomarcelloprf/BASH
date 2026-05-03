import type { TimeEntry } from "../../types";

interface Props { entry: TimeEntry; onDelete: (id: number) => void }

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "agora";
  if (m < 60) return `${m}min`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

export function EntryItem({ entry, onDelete }: Props) {
  return (
    <div className="flex items-start gap-3 py-3 border-b border-[#f0f0f0] last:border-0">
      <span className="font-mono font-bold text-sm text-[#111] w-10 shrink-0">
        {entry.hours}h
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-[#333] truncate">{entry.activity ?? "—"}</p>
        <p className="text-xs text-[#999] mt-0.5">{relativeTime(entry.created_at)}</p>
      </div>
      <button
        onClick={() => onDelete(entry.id)}
        className="text-[#aaa] hover:text-[#333] text-sm leading-none mt-0.5 shrink-0"
        aria-label="Remover"
      >
        ×
      </button>
    </div>
  );
}
