ALTER TABLE operations ADD COLUMN batch_id TEXT;
ALTER TABLE operations ADD COLUMN segment_id TEXT;
ALTER TABLE operations ADD COLUMN transaction_group_id TEXT;

ALTER TABLE receivables ADD COLUMN created_at TEXT;
ALTER TABLE receivables ADD COLUMN closed_at TEXT;

CREATE TABLE IF NOT EXISTS batch_inputs (
    id TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES pilot_sessions(id) ON DELETE CASCADE,
    input_mode TEXT NOT NULL CHECK (input_mode IN ('TEXT_SINGLE', 'TEXT_BATCH', 'VOICE_TRANSCRIPT')),
    source_text TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('READY', 'PARTIALLY_READY', 'NEEDS_REVIEW', 'BLOCKED')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS batch_items (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES batch_inputs(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    source_start INTEGER NOT NULL CHECK (source_start >= 0),
    source_end INTEGER NOT NULL CHECK (source_end > source_start),
    source_text TEXT NOT NULL,
    interpretation_state TEXT NOT NULL,
    confirmable INTEGER NOT NULL CHECK (confirmable IN (0, 1)),
    transaction_group_id TEXT,
    interpretation_json TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'PROPOSED'
        CHECK (lifecycle_status IN ('PROPOSED', 'CORRECTED', 'CONFIRMED', 'REJECTED', 'CANCELLED')),
    UNIQUE(batch_id, ordinal, id)
);

CREATE TABLE IF NOT EXISTS transaction_groups (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES batch_inputs(id) ON DELETE CASCADE,
    group_kind TEXT NOT NULL,
    customer_label TEXT,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS batch_confirmations (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES batch_inputs(id) ON DELETE CASCADE,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES pilot_sessions(id) ON DELETE CASCADE,
    idempotency_key TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PARTIALLY_CONFIRMED', 'CONFIRMED')),
    confirmed_at TEXT NOT NULL,
    UNIQUE(participant_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS batch_confirmation_items (
    confirmation_id TEXT NOT NULL REFERENCES batch_confirmations(id) ON DELETE CASCADE,
    item_id TEXT NOT NULL REFERENCES batch_items(id) ON DELETE CASCADE,
    operation_id TEXT NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    PRIMARY KEY (confirmation_id, item_id)
);

CREATE TABLE IF NOT EXISTS payment_allocations (
    id TEXT PRIMARY KEY,
    payment_operation_id TEXT NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    receivable_id TEXT NOT NULL REFERENCES receivables(id) ON DELETE CASCADE,
    amount_minor INTEGER NOT NULL CHECK (amount_minor > 0),
    previous_balance_minor INTEGER NOT NULL CHECK (previous_balance_minor >= 0),
    new_balance_minor INTEGER NOT NULL CHECK (new_balance_minor >= 0),
    created_at TEXT NOT NULL,
    UNIQUE(payment_operation_id, receivable_id)
);

CREATE TABLE IF NOT EXISTS receivable_movements (
    id TEXT PRIMARY KEY,
    receivable_id TEXT NOT NULL REFERENCES receivables(id) ON DELETE CASCADE,
    operation_id TEXT NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    movement_type TEXT NOT NULL CHECK (movement_type IN ('CREATED', 'PAYMENT')),
    amount_minor INTEGER NOT NULL CHECK (amount_minor > 0),
    previous_balance_minor INTEGER NOT NULL CHECK (previous_balance_minor >= 0),
    new_balance_minor INTEGER NOT NULL CHECK (new_balance_minor >= 0),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS operation_line_items (
    id TEXT PRIMARY KEY,
    operation_id TEXT NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    payload_json TEXT NOT NULL,
    UNIQUE(operation_id, ordinal)
);

CREATE TABLE IF NOT EXISTS batch_audit_events (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES batch_inputs(id) ON DELETE CASCADE,
    item_id TEXT REFERENCES batch_items(id) ON DELETE CASCADE,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    occurred_at TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN (
        'BATCH_SUBMITTED', 'BATCH_SEGMENTED', 'ITEM_INTERPRETED',
        'ITEM_CONTEXT_REQUESTED', 'ITEM_CORRECTED', 'ITEM_REJECTED',
        'ITEM_CONFIRMED', 'BATCH_PARTIALLY_CONFIRMED', 'BATCH_CONFIRMED'
    )),
    details_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_batch_inputs_participant
ON batch_inputs(participant_id, created_at);

CREATE INDEX IF NOT EXISTS idx_batch_items_batch
ON batch_items(batch_id, ordinal);

CREATE INDEX IF NOT EXISTS idx_transaction_groups_batch
ON transaction_groups(batch_id);

CREATE INDEX IF NOT EXISTS idx_allocations_receivable
ON payment_allocations(receivable_id, created_at);

CREATE INDEX IF NOT EXISTS idx_receivable_movements_receivable
ON receivable_movements(receivable_id, created_at);
