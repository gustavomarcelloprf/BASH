import { useEntries } from "../../hooks/useEntries";
import { EntryItem } from "./EntryItem";

export function EntryList() {
  const { entries, isLoading, deleteEntry } = useEntries();
  const sorted = [...entries].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  if (isLoading) return <p className="text-xs text-[#999] p-4">carregando…</p>;

  if (sorted.length === 0) {
    return (
      <p className="text-xs text-[#aaa] text-center py-12">nenhum registro ainda</p>
    );
  }

  return (
    <div className="px-4">
      {sorted.map((e) => (
        <EntryItem key={e.id} entry={e} onDelete={(id) => deleteEntry.mutate(id)} />
      ))}
    </div>
  );
}
