"use client";

import { useState } from "react";
import { BatchReview } from "@/components/BatchReview";
import { VoiceTranscriptReview } from "@/components/VoiceTranscriptReview";
import { api } from "@/lib/api";
import { createIdempotencyKey } from "@/lib/idempotency";
import type { BatchInterpretation } from "@/lib/types";

interface BatchWorkspaceProps {
  onConfirmed: () => Promise<void>;
}

const voiceEnabled = process.env.NEXT_PUBLIC_VOICE_EXPERIMENT === "true";

export function BatchWorkspace({ onConfirmed }: BatchWorkspaceProps) {
  const [text, setText] = useState("");
  const [inputMode, setInputMode] = useState<BatchInterpretation["input_mode"]>("TEXT_BATCH");
  const [batch, setBatch] = useState<BatchInterpretation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function interpret() {
    setLoading(true);
    setError("");
    setNotice("");
    try {
      setBatch(await api.interpretBatch(text, inputMode));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude separar los movimientos.");
    } finally {
      setLoading(false);
    }
  }

  async function correct(itemId: string, changes: Record<string, string | number | null>) {
    if (!batch) return;
    setLoading(true);
    setError("");
    try {
      const result = await api.correctBatchItem(batch.batch_id, itemId, changes);
      setBatch(result.batch);
      setNotice("Corregí solo ese renglón; los demás conservaron su interpretación.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude corregir ese movimiento.");
    } finally {
      setLoading(false);
    }
  }

  async function reject(itemId: string) {
    if (!batch) return;
    setLoading(true);
    setError("");
    try {
      const result = await api.rejectBatchItem(batch.batch_id, itemId);
      setBatch(result.batch);
      setNotice("Ese renglón quedó fuera y no se registrará.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude descartar ese movimiento.");
    } finally {
      setLoading(false);
    }
  }

  async function confirmSafe() {
    if (!batch) return;
    setLoading(true);
    setError("");
    try {
      const result = await api.confirmBatch(
        batch.batch_id, batch.confirmable_item_ids, createIdempotencyKey(),
      );
      setNotice(`${result.operations.length} movimientos confirmados y registrados.`);
      setBatch(null);
      setText("");
      setInputMode("TEXT_BATCH");
      await onConfirmed();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No pude registrar el lote.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <form className="entry-composer batch-composer" onSubmit={(event) => { event.preventDefault(); void interpret(); }}>
        <label htmlFor="batch-text">¿Qué pasó en el negocio?</label>
        <p id="batch-help">Escribe varias ventas, gastos, fiados o abonos tal como los recuerdas. Separaré solo lo que sea seguro.</p>
        <textarea
          id="batch-text"
          value={text}
          onChange={(event) => { setText(event.target.value); setInputMode("TEXT_BATCH"); }}
          placeholder="Ejemplo: Vendí panes, María quedó debiendo doce y gasté cuatro en transporte"
          aria-describedby="batch-help"
          rows={7}
          maxLength={2000}
          disabled={loading}
        />
        <div className="composer-footer">
          <span>{text.length}/2000 · hasta 20 movimientos</span>
          <button className="primary-action" type="submit" disabled={!text.trim() || loading}>
            {loading ? "Leyendo renglones…" : "Encontrar movimientos"}
          </button>
        </div>
      </form>
      {voiceEnabled && (
        <VoiceTranscriptReview
          disabled={loading}
          onAccept={(transcript) => { setText(transcript); setInputMode("VOICE_TRANSCRIPT"); setBatch(null); }}
        />
      )}
      {error && <p className="message error-message" role="alert">{error}</p>}
      {notice && <p className="message success-message" role="status">{notice}</p>}
      {batch && (
        <BatchReview
          batch={batch}
          disabled={loading}
          onCorrect={correct}
          onReject={reject}
          onConfirmSafe={confirmSafe}
        />
      )}
    </>
  );
}
