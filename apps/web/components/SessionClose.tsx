import type { FormEvent } from "react";

export interface SessionFeedback {
  annoying: string;
  missing: string;
  distrust: string;
  faster: string;
}

interface SessionCloseProps {
  feedback: SessionFeedback;
  loading: boolean;
  onChange: (field: keyof SessionFeedback, value: string) => void;
  onSubmit: () => void;
}

export function SessionClose({ feedback, loading, onChange, onSubmit }: SessionCloseProps) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <details className="session-close">
      <summary>Terminar sesión</summary>
      <form onSubmit={submit}>
        <p>El comentario es opcional y se guarda separado de las operaciones.</p>
        <label htmlFor="feedback-annoying">¿Qué fue molesto?</label>
        <input id="feedback-annoying" value={feedback.annoying} onChange={(event) => onChange("annoying", event.target.value)} maxLength={500} />
        <label htmlFor="feedback-missing">¿Qué faltó?</label>
        <input id="feedback-missing" value={feedback.missing} onChange={(event) => onChange("missing", event.target.value)} maxLength={500} />
        <label htmlFor="feedback-distrust">¿Qué te hizo desconfiar?</label>
        <input id="feedback-distrust" value={feedback.distrust} onChange={(event) => onChange("distrust", event.target.value)} maxLength={500} />
        <label htmlFor="feedback-faster">¿Qué fue más rápido que tu método actual?</label>
        <input id="feedback-faster" value={feedback.faster} onChange={(event) => onChange("faster", event.target.value)} maxLength={500} />
        <button className="secondary-action" type="submit" disabled={loading}>Guardar comentario y cerrar</button>
      </form>
    </details>
  );
}
