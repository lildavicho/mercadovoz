PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS operations (
    id TEXT PRIMARY KEY,
    proposal_id TEXT UNIQUE NOT NULL,
    operation_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    original_text TEXT,
    confirmed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_references (
    id TEXT PRIMARY KEY,
    label TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS product_references (
    id TEXT PRIMARY KEY,
    label TEXT UNIQUE NOT NULL,
    default_unit TEXT
);

CREATE TABLE IF NOT EXISTS receivables (
    id TEXT PRIMARY KEY,
    customer_label TEXT NOT NULL,
    original_amount REAL NOT NULL CHECK (original_amount > 0),
    balance REAL NOT NULL CHECK (balance >= 0),
    status TEXT NOT NULL CHECK (status IN ('OPEN', 'PAID')),
    source_operation_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS context_sessions (
    id TEXT PRIMARY KEY,
    snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    invalidated_at TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    action TEXT NOT NULL,
    details_json TEXT NOT NULL
);
