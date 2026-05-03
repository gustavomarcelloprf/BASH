import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { AdminUser, RoiData } from "../types";

export function useAdminData() {
  const { data: users, isLoading: usersLoading } = useQuery<AdminUser[]>({
    queryKey: ["admin", "users"],
    queryFn: async () => {
      const { data } = await api.get("/api/users");
      return data;
    },
    refetchInterval: 60_000,
  });

  const { data: roi, isLoading: roiLoading } = useQuery<RoiData>({
    queryKey: ["admin", "roi"],
    queryFn: async () => {
      const { data } = await api.get("/api/dashboard/roi");
      return data;
    },
    refetchInterval: 60_000,
  });

  return { users, roi, isLoading: usersLoading || roiLoading };
}
