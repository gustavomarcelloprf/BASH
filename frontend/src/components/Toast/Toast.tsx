import { useEffect } from "react";
import { useToastStore } from "../../stores/toast";

export function Toast() {
  const { message, type, visible, hide } = useToastStore();

  useEffect(() => {
    if (!visible) return;
    const timer = setTimeout(hide, 4000);
    return () => clearTimeout(timer);
  }, [visible, message, hide]);

  if (!visible) return null;

  return (
    <div
      style={{
        position: "fixed",
        bottom: "max(1rem, env(safe-area-inset-bottom))",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 1000,
        background: "#fff",
        border: type === "error" ? "1.5px solid #333" : "1.5px solid #111",
        borderRadius: "6px",
        padding: "12px 20px",
        fontSize: "14px",
        color: "#111",
        maxWidth: "360px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.10)",
      }}
      role="status"
      aria-live="polite"
    >
      {message}
    </div>
  );
}
