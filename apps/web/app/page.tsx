"use client";

import { useCallback, useEffect, useState } from "react";
import { DecisionBar } from "@/components/DecisionBar";
import { EntryComposer } from "@/components/EntryComposer";
import { LedgerHeader } from "@/components/LedgerHeader";
import { LedgerHistory } from "@/components/LedgerHistory";
import { OperationSlip } from "@/components/OperationSlip";
import { PilotAccessGate } from "@/components/PilotAccessGate";
import { PilotConsent } from "@/components/PilotConsent";
import { SessionClose, type SessionFeedback } from "@/components/SessionClose";
import { api } from "@/lib/api";
import { createIdempotencyKey } from "@/lib/idempotency";
import type {
  Interpretation,
  PilotConfig,
  PilotSession,
  Proposal,
  Receivable,
  StoredOperation,
} from "@/lib/types";

type PilotStage = "loading" | "access" | "consent" | "active" | "ended";

const emptyFeedback: SessionFeedback = { annoying: "", missing: "", distrust: "", faster: "" };

function deviceClass() {
  if (window.innerWidth < 768) return "mobile";
  if (window.innerWidth < 1024) return "tablet";
  return "desktop";
}

export default function Home() {
  const [stage, setStage] = useState<PilotStage>("loading");
  const [config, setConfig] = useState<PilotConfig | null>(null);
  const [participantId, setParticipantId] = useState("");
  const [accessCode, setAccessCode] = useState("");
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [session, setSession] = useState<PilotSession | null>(null);
  const [text, setText] = useState("");
  const [result, setResult] = useState<Interpretation | Proposal | null>(null);
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [correction, setCorrection] = useState("");
  const [correcting, setCorrecting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [operations, setOperations] = useState<StoredOperation[]>([]);
  const [receivables, setReceivables] = useState<Receivable[]>([]);
  const [feedback, setFeedback] = useState<SessionFeedback>(emptyFeedback);

  useEffect(() => {
    api.config()
      .then((value) => { setConfig(value); setStage("access"); })
      .catch(() => { setError("No pude conectar con el piloto privado."); setStage("access"); });
  }, []);

  const refreshLedger = useCallback(async () => {
    const [history, debts] = await Promise.all([api.operations(), api.receivables()]);
    setOperations(history);
    setReceivables(debts);
  }, []);

  async function requestAccess() {
    setLoading(true);
    setError(null);
    try {
      const access = await api.access(participantId, accessCode);
      setParticipantId(access.participant_id);
      setAccessCode("");
      setStage("consent");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude comprobar el acceso.");
    } finally {
      setLoading(false);
    }
  }

  async function acceptConsent() {
    if (!config) return;
    setLoading(true);
    setError(null);
    try {
      const opened = await api.consent(config.consent_version, deviceClass());
      setSession(opened);
      setStage("active");
      await refreshLedger();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude abrir la sesión.");
    } finally {
      setLoading(false);
    }
  }

  async function understand() {
    setLoading(true);
    setError(null);
    setNotice(null);
    try {
      const interpretation = await api.interpret(text);
      if ("proposal_id" in interpretation) {
        setProposal(interpretation);
      } else {
        setProposal(null);
      }
      setResult(interpretation);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude interpretar la operación.");
    } finally {
      setLoading(false);
    }
  }

  async function confirm() {
    if (!proposal) return;
    setLoading(true);
    setError(null);
    try {
      const confirmed = await api.confirm(proposal.proposal_id, createIdempotencyKey());
      setProposal(confirmed);
      setResult(confirmed);
      setNotice("Operación confirmada y registrada.");
      setText("");
      await refreshLedger();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude registrar la operación.");
    } finally {
      setLoading(false);
    }
  }

  async function applyCorrection() {
    if (!proposal || !correction.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const corrected = await api.correct(proposal.proposal_id, correction);
      setProposal(corrected);
      setResult(corrected);
      setCorrection("");
      setCorrecting(false);
      setNotice("Corrección registrada. Revisa la boleta antes de confirmar.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude aplicar la corrección.");
    } finally {
      setLoading(false);
    }
  }

  function clearProposal(message: string) {
    setProposal(null);
    setResult(null);
    setCorrection("");
    setCorrecting(false);
    setNotice(message);
  }

  async function cancel() {
    if (proposal) await api.cancel(proposal.proposal_id);
    clearProposal("Propuesta cancelada. No se registró nada.");
  }

  async function reject() {
    if (proposal) await api.reject(proposal.proposal_id);
    clearProposal("Propuesta marcada como incorrecta. No se registró nada.");
  }

  async function closeSession() {
    setLoading(true);
    setError(null);
    try {
      if (Object.values(feedback).some((value) => value.trim())) await api.feedback(feedback);
      await api.endSession();
      api.clearSession();
      setSession(null);
      setStage("ended");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude cerrar la sesión.");
    } finally {
      setLoading(false);
    }
  }

  const canDecide = Boolean(proposal && proposal.lifecycle_status !== "CONFIRMED");

  return (
    <main className="app-shell" id="main-content">
      <LedgerHeader participantId={stage === "active" ? participantId : undefined} />
      {stage === "loading" && <p className="loading-note" role="status">Preparando el cuaderno privado…</p>}
      {stage === "access" && (
        <PilotAccessGate
          participantId={participantId}
          accessCode={accessCode}
          loading={loading}
          error={error}
          onParticipantChange={setParticipantId}
          onCodeChange={setAccessCode}
          onSubmit={requestAccess}
        />
      )}
      {stage === "consent" && config && (
        <PilotConsent
          participantId={participantId}
          consentVersion={config.consent_version}
          accepted={consentAccepted}
          loading={loading}
          error={error}
          onAcceptedChange={setConsentAccepted}
          onContinue={acceptConsent}
        />
      )}
      {stage === "active" && session && (
        <>
          <div className="session-strip" aria-label="Sesión activa">
            <span>{participantId}</span>
            <span>Texto</span>
            <span>{session.pilot_version}</span>
          </div>
          <div className="workspace">
            <section className="capture-column" aria-label="Registrar operación">
              <EntryComposer value={text} isLoading={loading} onChange={setText} onSubmit={understand} />
              {error && <p className="message error-message" role="alert">{error}</p>}
              {notice && <p className="message success-message" role="status">{notice}</p>}
              {result && <OperationSlip result={result} />}
              {proposal && correcting && (
                <form className="correction-form" onSubmit={(event) => { event.preventDefault(); applyCorrection(); }}>
                  <label htmlFor="correction">¿Qué debo corregir?</label>
                  <p>Ejemplos: “eran seis”, “eran doce dólares”, “era tomate” o “no era María, era Rosa”.</p>
                  <div>
                    <input
                      id="correction"
                      value={correction}
                      onChange={(event) => setCorrection(event.target.value)}
                      placeholder="Escribe solo la corrección"
                      autoFocus
                      maxLength={200}
                    />
                    <button type="submit" disabled={!correction.trim() || loading}>Aplicar</button>
                  </div>
                </form>
              )}
              {proposal && proposal.lifecycle_status !== "CONFIRMED" && (
                <DecisionBar
                  disabled={loading || !canDecide}
                  correcting={correcting}
                  onConfirm={confirm}
                  onCorrect={() => setCorrecting((value) => !value)}
                  onReject={reject}
                  onCancel={cancel}
                />
              )}
              <SessionClose
                feedback={feedback}
                loading={loading}
                onChange={(field, value) => setFeedback((current) => ({ ...current, [field]: value }))}
                onSubmit={closeSession}
              />
            </section>
            <LedgerHistory operations={operations} receivables={receivables} onLoadAudit={api.audit} />
          </div>
        </>
      )}
      {stage === "ended" && (
        <section className="pilot-gate ended-sheet" aria-labelledby="ended-title">
          <p className="eyebrow">Sesión cerrada</p>
          <h2 id="ended-title">Gracias por usar el piloto</h2>
          <p>La sesión terminó y este navegador ya no conserva acceso. Para otra sesión, vuelve a abrir la página y usa tu invitación.</p>
        </section>
      )}
      <footer>
        MercadoVoz — Piloto privado · Motor congelado · Validación de campo pendiente
      </footer>
    </main>
  );
}
