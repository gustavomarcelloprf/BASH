import { useRef, useState } from "react";
import { api } from "../../lib/api";

type ImportState = "idle" | "dragover" | "uploading" | "done" | "error";

interface ImportResult {
  imported: number;
  skipped: number;
  duplicates: number;
}

export function ImportPanel() {
  const [state, setState] = useState<ImportState>("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const upload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      setErrorMsg("apenas arquivos .xlsx são aceitos");
      setState("error");
      return;
    }

    setState("uploading");
    setProgress(0);

    let pct = 0;
    timerRef.current = setInterval(() => {
      pct = Math.min(pct + 10, 90);
      setProgress(pct);
    }, 200);

    try {
      const form = new FormData();
      form.append("file", file);
      const { data } = await api.post("/api/import/excel", form);
      clearInterval(timerRef.current!);
      setProgress(100);
      setResult({ imported: data.imported, skipped: data.skipped, duplicates: data.duplicates });
      setTimeout(() => setState("done"), 350);
    } catch (err: unknown) {
      clearInterval(timerRef.current!);
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      setErrorMsg(typeof detail === "string" ? detail : "erro ao importar arquivo");
      setState("error");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setState("idle");
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) upload(file);
    e.target.value = "";
  };

  if (state === "done" && result) {
    return (
      <p className="text-[13px] text-[#333] py-3">
        {result.imported} importadas
        <span className="text-[#aaa]"> · </span>
        {result.skipped} ignoradas
        <span className="text-[#aaa]"> · </span>
        {result.duplicates} duplicatas
      </p>
    );
  }

  if (state === "uploading") {
    return (
      <div className="py-3">
        <p className="text-[13px] text-[#999]">importando...</p>
        <div className="h-[3px] bg-[#f0f0f0] mt-4 w-full">
          <div
            className="h-[3px] bg-[#333] transition-[width] duration-[350ms]"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div
        className="border border-dashed border-[#e5e5e5] px-4 py-8 text-center cursor-pointer"
        aria-label="área de upload de arquivo"
        onClick={() => {
          setState("idle");
          setErrorMsg("");
          inputRef.current?.click();
        }}
      >
        <p className="text-[13px] text-[#333]">{errorMsg}</p>
        <p className="text-[11px] text-[#aaa] mt-1">clique para tentar novamente</p>
        <input ref={inputRef} type="file" accept=".xlsx" hidden onChange={handleFile} />
      </div>
    );
  }

  return (
    <div
      className={`border px-4 py-8 text-center cursor-pointer transition-colors duration-200 ${
        state === "dragover"
          ? "border-solid border-[#111] bg-[#f9f9f9]"
          : "border-dashed border-[#e5e5e5]"
      }`}
      aria-label="área de upload de arquivo"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setState("dragover");
      }}
      onDragLeave={() => setState("idle")}
      onDrop={handleDrop}
    >
      <p className="text-[13px] text-[#999]">arraste um .xlsx aqui ou clique para selecionar</p>
      <input ref={inputRef} type="file" accept=".xlsx" hidden onChange={handleFile} />
    </div>
  );
}
