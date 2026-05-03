import { Navigate } from "react-router-dom";
import { useAuthStore } from "../stores/auth";

interface Props {
  role?: "admin" | "member";
  children: React.ReactNode;
}

export function ProtectedRoute({ role, children }: Props) {
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);

  if (!token) return <Navigate to="/login" replace />;
  if (!user) return null;
  if (role === "admin" && user.role !== "admin") return <Navigate to="/" replace />;
  return <>{children}</>;
}
