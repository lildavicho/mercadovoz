import { BatchItemCard } from "@/components/BatchItemCard";
import type { BatchInterpretation } from "@/lib/types";

interface BatchReviewProps {
  batch: BatchInterpretation;
  disabled: boolean;
  onCorrect: (itemId: string, changes: Record<string, string | number | null>) => Promise<void>;
  onReject: (itemId: string) => Promise<void>;
  onConfirmSafe: () => Promise<void>;
}

export function BatchReview({ batch, disabled, onCorrect, onReject, onConfirmSafe }: BatchReviewProps) {
  const ready = batch.confirmable_item_ids.length;
  const pending = batch.segments.length - ready;
  return (
    <section className="batch-review" aria-labelledby="batch-review-title">
      <header className="batch-review-heading">
        <div>
          <p className="eyebrow">Lectura por renglones</p>
          <h2 id="batch-review-title">Entendí {batch.segments.length} movimientos</h2>
        </div>
        <p aria-live="polite"><strong>{ready} listos</strong><span>{pending} por revisar</span></p>
      </header>
      <ol className="batch-list">
        {batch.segments.map((item, index) => (
          <li key={item.segment_id}>
            <BatchItemCard
              item={item}
              position={index + 1}
              disabled={disabled}
              onCorrect={onCorrect}
              onReject={onReject}
            />
          </li>
        ))}
      </ol>
      <div className="batch-decision-bar" aria-label="Decidir sobre movimientos seguros">
        {pending > 0 && <a href={`#batch-item-${batch.segments.find((item) => !item.confirmable)?.segment_id}`}>Revisar {pending} pendientes</a>}
        <button className="confirm-action" type="button" onClick={() => void onConfirmSafe()} disabled={disabled || ready === 0}>
          Confirmar {ready} {ready === 1 ? "movimiento listo" : "movimientos listos"}
        </button>
        <p>Ningún pendiente se registrará.</p>
      </div>
    </section>
  );
}
