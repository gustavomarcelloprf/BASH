import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { AdminUser } from "../../types";
import { api } from "../../lib/api";
import { useToastStore } from "../../stores/toast";

interface Props {
  user: AdminUser;
  currentUserId: number;
}

export function UserRow({ user, currentUserId }: Props) {
  const qc = useQueryClient();
  const toast = useToastStore();
  const [confirmAction, setConfirmAction] = useState<"deactivate" | "delete" | null>(null);

  const roleMutation = useMutation({
    mutationFn: (role: string) =>
      api.patch(`/api/users/${user.id}/role`, { role }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.show("função atualizada", "success");
    },
    onError: () => toast.show("erro ao atualizar função", "error"),
  });

  const statusMutation = useMutation({
    mutationFn: (is_active: boolean) =>
      api.patch(`/api/users/${user.id}/status`, { is_active }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.show(user.is_active ? "usuário desativado" : "usuário aprovado", "success");
      setConfirmAction(null);
    },
    onError: () => {
      toast.show("erro ao atualizar status", "error");
      setConfirmAction(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/api/users/${user.id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.show("usuário removido", "success");
      setConfirmAction(null);
    },
    onError: () => {
      toast.show("erro ao remover usuário", "error");
      setConfirmAction(null);
    },
  });

  const isPending = roleMutation.isPending || statusMutation.isPending || deleteMutation.isPending;
  const isSelf = user.id === currentUserId;
  const nextRole = user.role === "admin" ? "member" : "admin";
  const roleActionLabel = user.role === "admin" ? "rebaixar" : "promover";

  return (
    <div className="flex items-start gap-3 px-4 py-3 border-b border-[#f0f0f0] hover:bg-[#f9f9f9] transition-colors duration-[120ms]">
      <div className="flex-1 min-w-0">
        <p className="text-[13px] font-medium text-[#333] truncate">{user.name}</p>
        <p className="text-[11px] text-[#999] truncate">{user.email}</p>
      </div>

      <div className="flex items-center gap-2 shrink-0 mt-0.5">
        <span className="font-mono text-[12px] tabular-nums text-[#666] w-10 text-right">
          {user.hours_this_month.toFixed(1)}h
        </span>

        <span
          className={`text-[9px] uppercase tracking-wider border px-1.5 py-0.5${
            user.role === "admin"
              ? " border-[#111] text-[#111]"
              : " border-[#e5e5e5] text-[#999]"
          }`}
        >
          {user.role}
        </span>

        {!user.is_active && (
          <span className="text-[9px] uppercase tracking-wider border border-amber-300 text-amber-600 px-1.5 py-0.5">
            pendente
          </span>
        )}
      </div>

      {!isSelf && (
        <div className="flex items-center gap-3 shrink-0 text-[11px] mt-0.5">
          {confirmAction ? (
            <>
              <span className="text-[#999]">confirmar?</span>
              <span
                className="text-[#333] cursor-pointer"
                onClick={() => {
                  if (confirmAction === "deactivate") statusMutation.mutate(false);
                  else deleteMutation.mutate();
                }}
              >
                sim
              </span>
              <span
                className="text-[#999] cursor-pointer"
                onClick={() => setConfirmAction(null)}
              >
                não
              </span>
            </>
          ) : (
            <>
              <span
                className={`cursor-pointer transition-colors duration-[120ms] ${
                  isPending ? "text-[#aaa] pointer-events-none" : "text-[#666] hover:text-[#111]"
                }`}
                onClick={() => !isPending && roleMutation.mutate(nextRole)}
              >
                {roleActionLabel}
              </span>

              <span
                className={`cursor-pointer transition-colors duration-[120ms] ${
                  isPending ? "text-[#aaa] pointer-events-none" : "text-[#999] hover:text-[#333]"
                }`}
                onClick={() => {
                  if (!isPending) {
                    if (!user.is_active) statusMutation.mutate(true);
                    else setConfirmAction("deactivate");
                  }
                }}
              >
                {user.is_active ? "desativar" : "aprovar"}
              </span>

              <span
                className={`cursor-pointer transition-colors duration-[120ms] ${
                  isPending ? "text-[#aaa] pointer-events-none" : "text-[#999] hover:text-red-500"
                }`}
                onClick={() => !isPending && setConfirmAction("delete")}
              >
                remover
              </span>
            </>
          )}
        </div>
      )}
    </div>
  );
}
