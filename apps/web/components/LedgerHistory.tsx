"use client";

import { useMemo, useState } from "react";
import type { Receivable, StoredOperation } from "@/lib/types";

const names: Record<string, string> = {
  SALE: "Venta",
  EXPENSE: "Gasto",
  RECEIVABLE: "Fiado creado",
  PAYMENT_RECEIVED: "Abono recibido",
};

interface LedgerHistoryProps {
  operations: StoredOperation[];
  receivables: Receivable[];
  onLoadAudit: (operationId: string) => Promise<Array<Record<string, unknown>>>;
}

function amount(item: StoredOperation) {
  return item.operation.total ?? item.operation.amount ?? 0;
}

function money(value: number) {
  return new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(value);
}

export function LedgerHistory({ operations, receivables, onLoadAudit }: LedgerHistoryProps) {
  const [auditFor, setAuditFor] = useState<string | null>(null);
  const [audit, setAudit] = useState<Array<Record<string, unknown>>>([]);
  const [auditError, setAuditError] = useState<string | null>(null);
  const totals = useMemo(() => operations.reduce<Record<string, number>>((result, item) => {
    result[item.type] = (result[item.type] ?? 0) + amount(item);
    return result;
  }, {}), [operations]);

  async function inspect(operationId: string) {
    if (auditFor === operationId) {
      setAuditFor(null);
      return;
    }
    setAuditError(null);
    try {
      setAudit(await onLoadAudit(operationId));
      setAuditFor(operationId);
    } catch {
      setAuditError("No pude abrir el registro de revisión.");
    }
  }

  return (
    <aside className="ledger-history" aria-labelledby="history-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Solo lo confirmado</p>
          <h2 id="history-title">Cuaderno del día</h2>
        </div>
        <span>{operations.length} registros</span>
      </div>
      {operations.length > 0 && (
        <dl className="day-summary" aria-label="Resumen de operaciones confirmadas">
          {(["SALE", "EXPENSE", "RECEIVABLE", "PAYMENT_RECEIVED"] as const).map((type) => (
            <div key={type}>
              <dt>{names[type]}</dt>
              <dd>{money(totals[type] ?? 0)}</dd>
            </div>
          ))}
        </dl>
      )}
      {receivables.some((item) => item.status === "OPEN") && (
        <section className="open-debts" aria-labelledby="debts-title">
          <h3 id="debts-title">Saldo actual por cobrar</h3>
          {receivables.filter((item) => item.status === "OPEN").map((item) => (
            <p key={item.id}><span>{item.customer_label}</span><strong>{money(item.balance)}</strong></p>
          ))}
        </section>
      )}
      {auditError && <p className="message error-message" role="alert">{auditError}</p>}
      {operations.length === 0 ? (
        <p className="empty-state">Las operaciones aparecen aquí solo después de confirmarlas.</p>
      ) : (
        <ol className="history-list">
          {operations.map((item) => (
            <li key={item.id}>
              <div className="history-main">
                <span className="history-titleline"><strong>{names[item.type] ?? item.type}</strong><b>{money(amount(item))}</b></span>
                <span>{item.original_text}</span>
                <span className="history-meta">
                  <time dateTime={item.confirmed_at}>
                    {new Intl.DateTimeFormat("es-EC", { hour: "2-digit", minute: "2-digit" }).format(new Date(item.confirmed_at))}
                  </time>
                  <span>Confirmada</span>
                </span>
                <button className="audit-action" type="button" onClick={() => inspect(item.id)} aria-expanded={auditFor === item.id}>
                  {auditFor === item.id ? "Cerrar revisión" : "Ver revisión"}
                </button>
                {auditFor === item.id && (
                  <ol className="audit-list" aria-label="Eventos de revisión">
                    {audit.map((event, index) => <li key={`${String(event.action)}-${index}`}>{String(event.action)}</li>)}
                  </ol>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
    </aside>
  );
}
