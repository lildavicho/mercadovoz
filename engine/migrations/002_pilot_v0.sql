CREATE TABLE IF NOT EXISTS participants (
    id TEXT PRIMARY KEY CHECK (id GLOB 'P[0-9][0-9]'),
    evidence_class TEXT NOT NULL CHECK (evidence_class = 'REAL_DEVELOPMENT'),
    created_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS consents (
    id TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    consent_given INTEGER NOT NULL CHECK (consent_given = 1),
    consent_version TEXT NOT NULL,
    consented_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS access_sessions (
    token_hash TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS pilot_sessions (
    id TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    pilot_version TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    ui_version TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    consent_version TEXT NOT NULL,
    device_class TEXT CHECK (device_class IN ('mobile', 'tablet', 'desktop', 'unknown')),
    input_mode TEXT NOT NULL CHECK (input_mode = 'TEXT'),
    event_count INTEGER NOT NULL DEFAULT 0 CHECK (event_count >= 0)
);

CREATE TABLE IF NOT EXISTS pilot_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'SESSION_STARTED', 'TEXT_SUBMITTED', 'INTERPRETATION_CREATED',
        'CONTEXT_REQUESTED', 'CONFIRMATION_SHOWN', 'OPERATION_CONFIRMED',
        'OPERATION_CORRECTED', 'OPERATION_REJECTED', 'OPERATION_CANCELLED',
        'ERROR_SHOWN', 'SESSION_ENDED'
    )),
    session_id TEXT NOT NULL REFERENCES pilot_sessions(id) ON DELETE CASCADE,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    input_id TEXT,
    occurred_at TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    duration_ms REAL CHECK (duration_ms IS NULL OR duration_ms >= 0)
);

CREATE TABLE IF NOT EXISTS pilot_feedback (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES pilot_sessions(id) ON DELETE CASCADE,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    submitted_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pilot_annotations (
    id TEXT PRIMARY KEY,
    input_id TEXT NOT NULL,
    participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    critical_financial_error INTEGER NOT NULL CHECK (critical_financial_error IN (0, 1)),
    note TEXT,
    annotated_at TEXT NOT NULL
);

ALTER TABLE operations ADD COLUMN participant_id TEXT REFERENCES participants(id);
ALTER TABLE operations ADD COLUMN session_id TEXT REFERENCES pilot_sessions(id);
ALTER TABLE operations ADD COLUMN input_id TEXT;
ALTER TABLE receivables ADD COLUMN participant_id TEXT REFERENCES participants(id);
ALTER TABLE receivables ADD COLUMN session_id TEXT REFERENCES pilot_sessions(id);

CREATE INDEX IF NOT EXISTS idx_operations_participant ON operations(participant_id, confirmed_at);
CREATE INDEX IF NOT EXISTS idx_events_participant ON pilot_events(participant_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_input ON pilot_events(input_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_receivables_participant ON receivables(participant_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_annotations_input_category ON pilot_annotations(input_id, category);
