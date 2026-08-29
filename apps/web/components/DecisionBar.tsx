interface DecisionBarProps {
  disabled: boolean;
  correcting: boolean;
  onConfirm: () => void;
  onCorrect: () => void;
  onReject: () => void;
  onCancel: () => void;
}

export function DecisionBar({ disabled, correcting, onConfirm, onCorrect, onReject, onCancel }: DecisionBarProps) {
  return (
    <div className="decision-bar" aria-label="Decidir sobre la propuesta">
      <button className="confirm-action" type="button" onClick={onConfirm} disabled={disabled}>
        Confirmar y registrar
      </button>
      <button className="secondary-action" type="button" onClick={onCorrect} disabled={disabled}>
        {correcting ? "Cerrar corrección" : "Corregir"}
      </button>
      <button className="secondary-action" type="button" onClick={onReject} disabled={disabled}>
        No corresponde
      </button>
      <button className="text-action" type="button" onClick={onCancel} disabled={disabled}>
        Cancelar
      </button>
    </div>
  );
}
