import { useQuery } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { api } from "../lib/api";
import type { ParseResult } from "../types";

export function useParser(text: string) {
  const [debounced] = useDebounce(text, 300);

  return useQuery<ParseResult>({
    queryKey: ["parse", debounced],
    queryFn: async () => {
      const { data } = await api.post("/api/entries/parse", { text: debounced });
      return data;
    },
    enabled: debounced.length > 3,
    staleTime: 30_000,
  });
}
