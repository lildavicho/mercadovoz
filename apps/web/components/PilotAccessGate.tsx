import type { FormEvent } from "react";

interface PilotAccessGateProps {
  participantId: string;
  accessCode: string;
  loading: boolean;
  error: string | null;
  onParticipantChange: (value: string) => void;
  onCodeChange: (value: string) => void;
  onSubmit: () => void;
}

export function PilotAccessGate({
  participantId,
  accessCode,
  loading,
  error,
  onParticipantChange,
  onCodeChange,
  onSubmit,
}: PilotAccessGateProps) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <section className="pilot-gate" aria-labelledby="access-title">
      <p className="eyebrow">Acceso por invitación</p>
      <h2 id="access-title">Abrir mi cuaderno piloto</h2>
      <p>Usa el identificador y código entregados por la persona operadora del piloto.</p>
      <form onSubmit={submit}>
        <label htmlFor="participant-id">Identificador de participante</label>
        <input
          id="participant-id"
          value={participantId}
          onChange={(event) => onParticipantChange(event.target.value.toUpperCase())}
          placeholder="P01"
          pattern="P[0-9]{2}"
          autoComplete="username"
          inputMode="text"
          required
          disabled={loading}
        />
        <label htmlFor="pilot-code">Código privado</label>
        <input
          id="pilot-code"
          type="password"
          value={accessCode}
          onChange={(event) => onCodeChange(event.target.value)}
          autoComplete="current-password"
          minLength={8}
          required
          disabled={loading}
        />
        {error && <p className="message error-message" role="alert">{error}</p>}
        <button className="primary-action gate-action" type="submit" disabled={loading || !/^P\d{2}$/.test(participantId) || accessCode.length < 8}>
          {loading ? "Comprobando…" : "Continuar"}
        </button>
      </form>
    </section>
  );
}
