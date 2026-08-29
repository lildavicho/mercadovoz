export function LedgerHeader({ participantId }: { participantId?: string }) {
  return (
    <header className="ledger-header">
      <div>
        <p className="eyebrow">Cuaderno operativo · piloto privado</p>
        <h1>MercadoVoz</h1>
      </div>
      <div className="status-stamp" aria-label="Estado de validación">
        <span aria-hidden="true" />
        {participantId ? `Sesión ${participantId}` : "Acceso restringido"}
      </div>
    </header>
  );
}
