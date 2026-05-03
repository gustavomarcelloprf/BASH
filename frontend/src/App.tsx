import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "./stores/auth";
import { api } from "./lib/api";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Admin from "./pages/Admin";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Toast } from "./components/Toast";

const qc = new QueryClient();

function Guard({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

function UserLoader() {
  useEffect(() => {
    const { token, user, setAuth } = useAuthStore.getState();
    if (token && !user) {
      api.get("/api/auth/me").then(({ data }) => setAuth(data, token)).catch(() => {});
    }
  }, []);
  return null;
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <UserLoader />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Guard><Home /></Guard>} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute role="admin">
                <Admin />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toast />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
