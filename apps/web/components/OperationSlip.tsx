import type { Interpretation, Operation, Proposal } from "@/lib/types";

const labels: Record<string, string> = {
  SALE: "Venta",
  EXPENSE: "Gasto",
  RECEIVABLE: "Cuenta por cobrar",
  PAYMENT_RECEIVED: "Abono recibido",
};

function money(value: number | null | undefined) {
  return value == null
    ? "—"
    : new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(value);
}

function Fields({ operation }: { operation: Operation }) {
  const rows = [
    ["Producto", operation.product],
    ["Cantidad", operation.quantity !== undefined ? `${operation.quantity} ${operation.unit ?? ""}` : undefined],
    ["Precio unitario", operation.unit_price != null ? money(operation.unit_price) : undefined],
    ["Total", operation.total !== undefined ? money(operation.total) : undefined],
    ["Categoría", operation.category],
    ["Persona", operation.customer],
    ["Importe", operation.amount !== undefined ? money(operation.amount) : undefined],
  ].filter((row): row is [string, string] => Boolean(row[1]));

  return (
    <dl className="operation-fields">
      {rows.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

interface OperationSlipProps {
  result: Interpretation | Proposal;
}

export function OperationSlip({ result }: OperationSlipProps) {
  const operation = result.operation;
  const displayStatus = "interpretation_status" in result
    ? result.lifecycle_status
    : result.status;
  return (
    <section className="operation-slip" aria-live="polite" aria-labelledby="slip-title">
      <div className="slip-topline">
        <span>{operation ? labels[operation.type] ?? operation.type : "Necesita atención"}</span>
        <strong>{displayStatus}</strong>
      </div>
      <h2 id="slip-title">Entendí esto</h2>
      {operation ? <Fields operation={operation} /> : <p className="no-operation">No propuse ninguna operación.</p>}
      <p className="slip-question">{result.question}</p>
      {result.warnings.length > 0 && (
        <details>
          <summary>Por qué necesito cuidado</summary>
          <ul>{result.warnings.map((warning) => <li key={warning}>{warning.replaceAll("_", " ")}</li>)}</ul>
        </details>
      )}
    </section>
  );
}
