# ADR-004 — SQLite WAL for the private pilot

**Status:** accepted for `pilot-v0`; hosting detail superseded by ADR-005.

## Context

The pilot starts with one operator and a small number of participants. It requires transactions, reproducible migrations, deletion, export and rollback, but there is no evidence that it needs concurrent application replicas.

## Options

SQLite WAL, managed PostgreSQL/Supabase, or JSONL-only storage were compared. PostgreSQL offers better concurrency but adds service, credentials and operational surface before that need exists. JSONL does not provide the relational and transactional guarantees required for balances and audit.

## Decision

Use SQLite WAL with versioned migrations and exactly one API instance. The database lives on persistent storage outside the checkout. Confirmation writes the operation and audit event in one transaction. JSONL exports preserve portability.

## Consequences

- Backup and restore are operator responsibilities.
- No horizontal replicas while SQLite remains active.
- A later migration to PostgreSQL is triggered by sustained concurrent writes, multiple API replicas, several operators or stronger point-in-time recovery needs.
- Hosting moved from the earlier Vercel/Railway preparation to Oracle Cloud in ADR-005; the storage decision itself remains unchanged.
