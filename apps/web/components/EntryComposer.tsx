import type { FormEvent, KeyboardEvent } from "react";

interface EntryComposerProps {
  value: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export function EntryComposer({ value, isLoading, onChange, onSubmit }: EntryComposerProps) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  function submitWithKeyboard(event: KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && value.trim() && !isLoading) {
      event.preventDefault();
      onSubmit();
    }
  }

  return (
    <form className="entry-composer" onSubmit={submit}>
      <label htmlFor="operation-text">¿Qué pasó en el negocio?</label>
      <p id="operation-help">Escribe una venta, gasto, deuda o abono. Una operación por vez.</p>
      <textarea
        id="operation-text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ejemplo: Vendí cinco libras de tomate a dos dólares cada una"
        aria-describedby="operation-help"
        rows={4}
        maxLength={500}
        disabled={isLoading}
        onKeyDown={submitWithKeyboard}
      />
      <div className="composer-footer">
        <span>{value.length}/500 · Ctrl + Enter</span>
        <button className="primary-action" type="submit" disabled={!value.trim() || isLoading}>
          {isLoading ? "Interpretando…" : "Entender operación"}
        </button>
      </div>
    </form>
  );
}
