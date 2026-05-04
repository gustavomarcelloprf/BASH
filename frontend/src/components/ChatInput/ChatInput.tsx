import { useState, type KeyboardEvent } from "react";
import { useParser } from "../../hooks/useParser";
import { useEntries } from "../../hooks/useEntries";
import { LivePreview } from "./LivePreview";

export function ChatInput() {
  const [text, setText] = useState("");
  const { data: preview, isFetching } = useParser(text);
  const { createEntry } = useEntries();

  const submit = () => {
    if (!preview || preview.hours === null) return;
    createEntry.mutate({
      project_id: 1,
      date: preview.date,
      hours: preview.hours,
      activity: preview.activity,
    });
    setText("");
  };

  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  const canSubmit = preview && preview.hours !== null;

  return (
    <div className="space-y-3">
      <input
        className="w-full bg-[#f9f9f9] border border-[#e5e5e5] rounded px-3 py-2 text-sm font-sans text-[#111] placeholder-[#aaa] outline-none focus:border-[#999]"
        placeholder="2h na petição do caso Silva…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKey}
        autoFocus
      />
      <LivePreview result={preview} loading={isFetching && text.length > 3} />
      {canSubmit && (
        <button
          onClick={submit}
          disabled={createEntry.isPending}
          className="text-[13px] px-4 py-1.5 bg-[#111] text-white rounded hover:bg-[#333] disabled:opacity-50 transition-colors duration-[120ms] cursor-pointer"
        >
          {createEntry.isPending ? "registrando…" : "registrar"}
        </button>
      )}
    </div>
  );
}
