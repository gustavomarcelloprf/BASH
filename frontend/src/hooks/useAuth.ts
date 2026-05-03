import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";

export function useAuth() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const toast = useToastStore();

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
    onError: () => toast.show("email ou senha incorretos", "error"),
  });

  return { login };
}
