import type { Proposal } from "./types";

const TERMINAL_LIFECYCLES = new Set(["CONFIRMED", "REJECTED", "CANCELLED"]);

export function isConfirmableProposal(proposal: Proposal | null): boolean {
  return Boolean(
    proposal
      && proposal.interpretation_status === "COMPLETE"
      && proposal.missing_fields.length === 0
      && !TERMINAL_LIFECYCLES.has(proposal.lifecycle_status),
  );
}

export function reviewActionLabel(status: string): "Completar información" | "Corregir" {
  return status === "NEEDS_CONTEXT" || status === "NEEDS_CONFIRMATION"
    ? "Completar información"
    : "Corregir";
}
