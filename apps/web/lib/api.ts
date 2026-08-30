import type {
  Interpretation,
  PilotAccess,
  PilotConfig,
  PilotSession,
  Proposal,
  Receivable,
  StoredOperation,
} from "./types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "").trim();

let accessToken = "";
let sessionId = "";

async function request<T>(path: string, init?: RequestInit, authenticated = true): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(authenticated && accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(authenticated && sessionId ? { "X-Pilot-Session": sessionId } : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const error = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(typeof error?.detail === "string" ? error.detail : "No se pudo completar la acción.");
  }
  return response.json() as Promise<T>;
}

export const api = {
  config: () => request<PilotConfig>("/pilot/config", undefined, false),
  access: async (participantId: string, code: string) => {
    const result = await request<PilotAccess>("/pilot/access", {
      method: "POST",
      body: JSON.stringify({ participant_id: participantId, access_code: code }),
    }, false);
    accessToken = result.access_token;
    return result;
  },
  consent: async (consentVersion: string, deviceClass: string) => {
    const result = await request<PilotSession>("/pilot/consent", {
      method: "POST",
      body: JSON.stringify({
        consent_given: true,
        consent_version: consentVersion,
        device_class: deviceClass,
      }),
    });
    sessionId = result.id;
    return result;
  },
  interpret: (text: string) =>
    request<Interpretation | Proposal>("/pilot/interpret", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
  correct: (id: string, text: string) =>
    request<Proposal>(`/pilot/proposals/${id}/correct`, {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
  confirm: (id: string, idempotencyKey: string) =>
    request<Proposal>(`/pilot/proposals/${id}/confirm`, {
      method: "POST",
      body: JSON.stringify({ idempotency_key: idempotencyKey }),
    }),
  cancel: (id: string) =>
    request<Proposal>(`/pilot/proposals/${id}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reason: "USER_DECISION" }),
    }),
  reject: (id: string) =>
    request<Proposal>(`/pilot/proposals/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason: "USER_REJECTED_PROPOSAL" }),
    }),
  operations: () => request<StoredOperation[]>("/pilot/operations"),
  receivables: () => request<Receivable[]>("/pilot/receivables"),
  audit: (operationId: string) => request<Array<Record<string, unknown>>>(`/pilot/operations/${operationId}/audit`),
  feedback: (payload: { annoying: string; missing: string; distrust: string; faster: string }) =>
    request("/pilot/feedback", { method: "POST", body: JSON.stringify(payload) }),
  endSession: () => request<PilotSession>("/pilot/session/end", { method: "POST" }),
  clearSession: () => {
    accessToken = "";
    sessionId = "";
  },
};
