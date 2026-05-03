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
  const [confirming, setConfirming] = useState(false);

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
      toast.show(user.is_active ? "usuário desativado" : "usuário ativado", "success");
      setConfirming(false);
    },
    onError: () => {
      toast.show("erro ao atualizar status", "error");
      setConfirming(false);
    },
  });

  const isPending = roleMutation.isPending || statusMutation.isPending;
  const isSelf = user.id === currentUserId;
  const nextRole = user.role === "admin" ? "member" : "admin";
  const roleActionLabel = user.role === "admin" ? "rebaixar" : "promover";

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 border-b border-[#f0f0f0] hover:bg-[#f9f9f9] transition-colors duration-[120ms]${
        !user.is_active ? " opacity-50" : ""
      }`}
    >
      <span
        className={`flex-1 text-[13px] font-medium text-[#333] truncate${
          !user.is_active ? " line-through" : ""
        }`}
      >
        {user.name}
      </span>

      <span className="font-mono text-[13px] tabular-nums text-[#666] w-10 text-right shrink-0">
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

      {!isSelf && (
        <div className="flex items-center gap-3 shrink-0 text-[11px]">
          <span
            className={`cursor-pointer transition-colors duration-[120ms] ${
              isPending ? "text-[#aaa] pointer-events-none" : "text-[#666] hover:text-[#111]"
            }`}
            onClick={() => !isPending && roleMutation.mutate(nextRole)}
          >
            {roleActionLabel}
          </span>

          {confirming ? (
            <>
              <span className="text-[#999]">confirmar?</span>
              <span
                className="text-[#333] cursor-pointer"
                onClick={() => statusMutation.mutate(false)}
              >
                sim
              </span>
              <span
                className="text-[#999] cursor-pointer"
                onClick={() => setConfirming(false)}
              >
                não
              </span>
            </>
          ) : (
            <span
              className={`cursor-pointer transition-colors duration-[120ms] ${
                isPending ? "text-[#aaa] pointer-events-none" : "text-[#999] hover:text-[#333]"
              }`}
              onClick={() =>
                !isPending &&
                (user.is_active ? setConfirming(true) : statusMutation.mutate(true))
              }
            >
              {user.is_active ? "desativar" : "ativar"}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
