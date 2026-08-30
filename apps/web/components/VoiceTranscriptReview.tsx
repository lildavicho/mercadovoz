"use client";

import { useRef, useState } from "react";
import { BrowserSpeechTranscriber, hasNumericTranscriptRisk, type SpeechTranscriber } from "@/lib/speech";

interface VoiceTranscriptReviewProps {
  disabled: boolean;
  onAccept: (text: string) => void;
  createTranscriber?: () => SpeechTranscriber;
}

export function VoiceTranscriptReview({
  disabled,
  onAccept,
  createTranscriber = () => new BrowserSpeechTranscriber(),
}: VoiceTranscriptReviewProps) {
  const transcriber = useRef<SpeechTranscriber | null>(null);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");

  function start() {
    setError("");
    setTranscript("");
    const next = createTranscriber();
    transcriber.current = next;
    setListening(true);
    next.start(
      (result) => {
        setTranscript(result.text);
        if (result.isFinal) setListening(false);
      },
      (message) => {
        setListening(false);
        setError(message);
      },
    );
  }

  function stop() {
    transcriber.current?.stop();
    setListening(false);
  }

  function cancel() {
    transcriber.current?.cancel();
    setListening(false);
    setTranscript("");
    setError("");
  }

  return (
    <section className="voice-experiment" aria-labelledby="voice-title">
      <div>
        <p className="eyebrow">Experimento local · no habilitado en P01_R2</p>
        <h3 id="voice-title">Dictar para obtener un borrador</h3>
      </div>
      <p>La transcripción nunca se registra sola. Revísala y edítala antes de enviarla al motor.</p>
      <div className="voice-controls">
        {!listening ? (
          <button type="button" className="secondary-action" onClick={start} disabled={disabled} aria-label="Comenzar dictado">
            <span aria-hidden="true">●</span> Hablar
          </button>
        ) : (
          <button type="button" className="secondary-action recording" onClick={stop} aria-label="Detener dictado">
            Detener grabación
          </button>
        )}
        <button type="button" className="text-action" onClick={cancel} disabled={!listening && !transcript}>
          Cancelar voz
        </button>
      </div>
      {listening && <p className="recording-status" role="status"><span aria-hidden="true">●</span> Escuchando…</p>}
      {error && <p className="message error-message" role="alert">{error}</p>}
      {transcript && (
        <div className="transcript-sheet">
          <label htmlFor="voice-transcript">Transcripción reconocida</label>
          <textarea
            id="voice-transcript"
            value={transcript}
            onChange={(event) => setTranscript(event.target.value)}
            rows={4}
            maxLength={2000}
          />
          {hasNumericTranscriptRisk(transcript) && (
            <p className="numeric-warning" role="status">⚠ Revisa con cuidado números, cantidades y dinero.</p>
          )}
          <div className="transcript-actions">
            <button type="button" className="primary-action" onClick={() => onAccept(transcript)} disabled={!transcript.trim()}>
              Usar esta transcripción
            </button>
            <button type="button" className="secondary-action" onClick={start}>Volver a grabar</button>
          </div>
        </div>
      )}
    </section>
  );
}
