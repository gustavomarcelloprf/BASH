import { create } from "zustand";

type ToastType = "error" | "success";

interface ToastState {
  message: string;
  type: ToastType;
  visible: boolean;
  show: (message: string, type: ToastType) => void;
  hide: () => void;
}

export const useToastStore = create<ToastState>((set) => ({
  message: "",
  type: "error",
  visible: false,
  show: (message, type) => set({ message, type, visible: true }),
  hide: () => set({ visible: false }),
}));
