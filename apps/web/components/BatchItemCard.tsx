"use client";

import { useState } from "react";
import type { BatchSegment, Operation } from "@/lib/types";

const operationLabels: Record<string, string> = {
  SALE: "Venta",
  EXPENSE: "Gasto",
  RECEIVABLE: "Fiado creado",
  PAYMENT_RECEIVED: "Abono recibido",
};

const editableFields = ["amount", "quantity", "product", "customer", "category", "unit", "unit_price", "total"] as const;

interface BatchItemCardProps {
  item: BatchSegment;
  position: number;
  disabled: boolean;
  onCorrect: (itemId: string, changes: Record<string, string | number | null>) => Promise<void>;
  onReject: (itemId: string) => Promise<void>;
}

function money(value: number | undefined) {
  return value === undefined ? null : new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(value);
}

function amountFor(operation: Operation | null) {
  return operation ? money(operation.total ?? operation.amount) : null;
}

export function BatchItemCard({ item, position, disabled, onCorrect, onReject }: BatchItemCardProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<Record<string, string>>({});
  const titleId = `batch-item-${item.segment_id}`;
  const status = item.confirmable ? "Listo para confirmar" : "Requiere revisión";

  function beginEditing() {
    const operation: Operation = item.operation ?? { type: "" };
    setDraft(Object.fromEntries(
      editableFields
        .filter((field) => operation[field] !== undefined)
        .map((field) => [field, String(operation[field] ?? "")]),
    ));
    setEditing(true);
  }

  async function save() {
    const numeric = new Set(["amount", "quantity", "unit_price", "total"]);
    const changes = Object.fromEntries(Object.entries(draft).map(([field, value]) => [
      field,
      numeric.has(field) ? (value.trim() ? Number(value) : null) : value.trim(),
    ]));
    await onCorrect(item.segment_id, changes);
    setEditing(false);
  }

  return (
    <article className={`batch-item ${item.confirmable ? "item-ready" : "item-review"}`} aria-labelledby={titleId}>
      <header className="batch-item-heading">
        <span className="item-sequence" aria-hidden="true">{position}</span>
        <div>
          <p className="item-status">{item.confirmable ? "✓" : "⚠"} {status}</p>
          <h3 id={titleId}>{item.operation ? operationLabels[item.operation.type] ?? item.operation.type : "Fragmento no resuelto"}</h3>
        </div>
        {amountFor(item.operation) && <strong>{amountFor(item.operation)}</strong>}
      </header>

      <blockquote className="source-ribbon">
        <span>Origen {item.source_span.start}–{item.source_span.end}</span>
        “{item.source_text}”
      </blockquote>

      {item.operation && (
        <dl className="batch-fields">
          {item.operation.customer && <div><dt>Cliente</dt><dd>{item.operation.customer}</dd></div>}
          {item.operation.product && <div><dt>Producto</dt><dd>{item.operation.product}</dd></div>}
          {item.operation.quantity !== undefined && <div><dt>Cantidad</dt><dd>{item.operation.quantity} {item.operation.unit}</dd></div>}
          {item.operation.unit_price !== undefined && item.operation.unit_price !== null && <div><dt>Precio unitario</dt><dd>{money(item.operation.unit_price)}</dd></div>}
          {item.operation.category && <div><dt>Categoría</dt><dd>{item.operation.category}</dd></div>}
          {item.operation.line_items?.map((line) => (
            <div key={line.line_item_id}>
              <dt>{line.product}</dt>
              <dd>{line.quantity} × {money(line.unit_price)} = {money(line.total)}</dd>
            </div>
          ))}
        </dl>
      )}

      {item.warnings.length > 0 && (
        <details>
          <summary>Por qué requiere atención</summary>
          <ul>{item.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
        </details>
      )}

      {editing && item.operation && (
        <form className="batch-correction" onSubmit={(event) => { event.preventDefault(); void save(); }}>
          <fieldset>
            <legend>Tipo de movimiento</legend>
            <div className="operation-choice">
              {Object.entries(operationLabels).map(([value, label]) => (
                <button
                  key={value}
                  type="button"
                  aria-pressed={(draft.type ?? item.operation?.type) === value}
                  onClick={() => setDraft((current) => ({ ...current, type: value }))}
                >
                  {label}
                </button>
              ))}
            </div>
          </fieldset>
          <div className="correction-grid">
            {editableFields.filter((field) => draft[field] !== undefined).map((field) => (
              <label key={field}>
                {field.replace("unit_price", "precio unitario").replace("amount", "monto").replace("quantity", "cantidad")}
                <input
                  value={draft[field]}
                  inputMode={(["amount", "quantity", "unit_price", "total"] as string[]).includes(field) ? "decimal" : "text"}
                  onChange={(event) => setDraft((current) => ({ ...current, [field]: event.target.value }))}
                />
              </label>
            ))}
          </div>
          <div className="item-actions">
            <button className="primary-action" type="submit" disabled={disabled}>Guardar corrección</button>
            <button className="secondary-action" type="button" onClick={() => setEditing(false)}>Cerrar</button>
          </div>
        </form>
      )}

      {!editing && (
        <div className="item-actions">
          {item.operation && <button className="secondary-action" type="button" onClick={beginEditing} disabled={disabled}>Corregir este movimiento</button>}
          <button className="text-action" type="button" onClick={() => void onReject(item.segment_id)} disabled={disabled}>No corresponde</button>
        </div>
      )}
    </article>
  );
}
