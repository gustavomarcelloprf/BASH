import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuthStore } from "../stores/auth";

export function useAuth() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const login = useMutation({
    mutationFn: async (creds: { email: string; password: string }) => {
      const { data: tokenData } = await api.post("/api/auth/login", creds);
      const { data: me } = await api.get("/api/auth/me", {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      });
      return { user: me, token: tokenData.access_token };
    },
    onSuccess: ({ user, token }) => {
      setAuth(user, token);
      navigate("/");
    },
  });

  const register = useMutation({
    mutationFn: (payload: { name: string; email: string; password: string }) =>
      api.post("/api/auth/register", payload),
  });

  return { login, register };
}
