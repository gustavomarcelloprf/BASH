import { create } from "zustand";
import type { User } from "../types";

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

const TOKEN_KEY = "dash_token";

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: sessionStorage.getItem(TOKEN_KEY),

  setAuth: (user, token) => {
    sessionStorage.setItem(TOKEN_KEY, token);
    set({ user, token });
  },

  logout: () => {
    sessionStorage.removeItem(TOKEN_KEY);
    set({ user: null, token: null });
  },
}));
