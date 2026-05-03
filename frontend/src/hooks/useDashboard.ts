import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { DashboardSummary } from "../types";

export function useDashboard() {
  return useQuery<DashboardSummary>({
    queryKey: ["dashboard", "summary"],
    queryFn: async () => {
      const { data } = await api.get("/api/dashboard/summary?period=month");
      return data;
    },
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
  });
}
