import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export interface Alert {
  project_id: number;
  project_name: string;
  budget_hours: number;
  consumed_hours: number;
  percent: number;
  status: "warning" | "critical";
}

export function useAlerts() {
  return useQuery<Alert[]>({
    queryKey: ["dashboard", "alerts"],
    queryFn: async () => {
      const { data } = await api.get("/api/dashboard/alerts");
      return data;
    },
    refetchInterval: 60_000,
  });
}
