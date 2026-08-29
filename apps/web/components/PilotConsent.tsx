interface PilotConsentProps {
  participantId: string;
  consentVersion: string;
  accepted: boolean;
  loading: boolean;
  error: string | null;
  onAcceptedChange: (value: boolean) => void;
  onContinue: () => void;
}

export function PilotConsent({
  participantId,
  consentVersion,
  accepted,
  loading,
  error,
  onAcceptedChange,
  onContinue,
}: PilotConsentProps) {
  return (
    <section className="pilot-gate consent-sheet" aria-labelledby="consent-title">
      <p className="eyebrow">Participante {participantId} · {consentVersion}</p>
      <h2 id="consent-title">Antes de registrar</h2>
      <div className="consent-copy">
        <p>MercadoVoz está en piloto privado y puede cometer errores. Revisa cada propuesta antes de guardarla.</p>
        <p>Guardaremos lo que escribas, la interpretación, tus correcciones y el resultado para evaluar y mejorar el sistema.</p>
        <p>No solicitamos cédulas, teléfonos, direcciones, información bancaria, ubicación, fotografías ni audio. Puedes dejar de participar y solicitar la eliminación de tus datos del piloto.</p>
      </div>
      <label className="consent-check">
        <input
          type="checkbox"
          checked={accepted}
          onChange={(event) => onAcceptedChange(event.target.checked)}
          disabled={loading}
        />
        <span>Entiendo el piloto y acepto participar con estas condiciones.</span>
      </label>
      {error && <p className="message error-message" role="alert">{error}</p>}
      <button className="primary-action gate-action" type="button" onClick={onContinue} disabled={!accepted || loading}>
        {loading ? "Abriendo sesión…" : "Aceptar y comenzar"}
      </button>
    </section>
  );
}
