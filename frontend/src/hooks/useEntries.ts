import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { useToastStore } from "../stores/toast";
import type { TimeEntry } from "../types";

export function useEntries() {
  const qc = useQueryClient();
  const toast = useToastStore();

  const { data: entries = [], isLoading } = useQuery<TimeEntry[]>({
    queryKey: ["entries"],
    queryFn: async () => {
      const { data } = await api.get("/api/entries?period=month");
      return data;
    },
  });

  const createEntry = useMutation({
    mutationFn: async (payload: Omit<TimeEntry, "id" | "user_id" | "created_at" | "source">) => {
      const { data } = await api.post("/api/entries", { ...payload, source: "chat" });
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["entries"] }),
    onError: () => toast.show("erro ao salvar entrada", "error"),
  });

  const deleteEntry = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/api/entries/${id}`);
    },
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: ["entries"] });
      const prev = qc.getQueryData<TimeEntry[]>(["entries"]);
      qc.setQueryData<TimeEntry[]>(["entries"], (old) => (old ?? []).filter((e) => e.id !== id));
      return { prev };
    },
    onError: (_e, _id, ctx) => {
      if (ctx?.prev) qc.setQueryData(["entries"], ctx.prev);
      toast.show("erro ao remover entrada", "error");
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["entries"] }),
  });

  return { entries, isLoading, createEntry, deleteEntry };
}
