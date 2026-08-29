from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from threading import RLock
from typing import Any
from uuid import uuid4

from .pilot_version import PILOT_EVENT_SCHEMA_VERSION


EVENT_TYPES = {
    "SESSION_STARTED",
    "TEXT_SUBMITTED",
    "INTERPRETATION_CREATED",
    "CONTEXT_REQUESTED",
    "CONFIRMATION_SHOWN",
    "OPERATION_CONFIRMED",
    "OPERATION_CORRECTED",
    "OPERATION_REJECTED",
    "OPERATION_CANCELLED",
    "ERROR_SHOWN",
    "SESSION_ENDED",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


class SQLiteLedger:
    """Single-instance pilot store with versioned migrations and tenant filters."""

    def __init__(self, path: str | Path = "mercadovoz.db") -> None:
        self.path = str(path)
        self._lock = RLock()
        self._closed = False
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA busy_timeout = 5000")
        self._initialize()

    def _initialize(self) -> None:
        migration_dir = Path(__file__).resolve().parents[2] / "migrations"
        with self._lock, self._connection:
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
            )
            applied = {
                row["version"]
                for row in self._connection.execute("SELECT version FROM schema_migrations")
            }
            for migration in sorted(migration_dir.glob("*.sql")):
                if migration.stem in applied:
                    continue
                self._connection.executescript(migration.read_text(encoding="utf-8"))
                self._connection.execute(
                    "INSERT INTO schema_migrations VALUES (?, ?)",
                    (migration.stem, _now()),
                )

    def health(self) -> bool:
        return self._connection.execute("SELECT 1").fetchone()[0] == 1

    def schema_versions(self) -> list[str]:
        return [
            row["version"]
            for row in self._connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            )
        ]

    # Access tokens are ephemeral credentials. Only their SHA-256 digests are stored.
    def create_access_session(self, participant_id: str, ttl_hours: int = 12) -> str:
        token = secrets.token_urlsafe(32)
        created = datetime.now(timezone.utc)
        with self._connection:
            self._connection.execute(
                "INSERT INTO access_sessions VALUES (?, ?, ?, ?, NULL)",
                (
                    _token_hash(token),
                    participant_id,
                    created.isoformat(),
                    (created + timedelta(hours=ttl_hours)).isoformat(),
                ),
            )
        return token

    def participant_for_token(self, token: str) -> str | None:
        if not token:
            return None
        row = self._connection.execute(
            "SELECT participant_id, expires_at, revoked_at FROM access_sessions WHERE token_hash = ?",
            (_token_hash(token),),
        ).fetchone()
        if row is None or row["revoked_at"]:
            return None
        if datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
            return None
        return str(row["participant_id"])

    def begin_pilot_session(
        self,
        *,
        participant_id: str,
        consent_version: str,
        versions: dict[str, str],
        device_class: str = "unknown",
    ) -> dict[str, Any]:
        started_at = _now()
        session_id = str(uuid4())
        with self._lock, self._connection:
            self._connection.execute(
                "INSERT OR IGNORE INTO participants VALUES (?, 'REAL_DEVELOPMENT', ?, NULL)",
                (participant_id, started_at),
            )
            self._connection.execute(
                "INSERT INTO consents VALUES (?, ?, 1, ?, ?, NULL)",
                (str(uuid4()), participant_id, consent_version, started_at),
            )
            self._connection.execute(
                """
                INSERT INTO pilot_sessions (
                    id, participant_id, pilot_version, engine_version, parser_version,
                    schema_version, ui_version, started_at, ended_at, consent_version,
                    device_class, input_mode, event_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, 'TEXT', 0)
                """,
                (
                    session_id,
                    participant_id,
                    versions["pilot_version"],
                    versions["engine_version"],
                    versions["parser_version"],
                    versions["schema_version"],
                    versions["ui_version"],
                    started_at,
                    consent_version,
                    device_class,
                ),
            )
            self._insert_event(
                self._connection,
                event_type="SESSION_STARTED",
                session_id=session_id,
                participant_id=participant_id,
                engine_version=versions["engine_version"],
                payload={"input_mode": "TEXT", "device_class": device_class},
            )
        return self.get_session(session_id, participant_id)

    def get_session(self, session_id: str, participant_id: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT * FROM pilot_sessions WHERE id = ? AND participant_id = ?",
            (session_id, participant_id),
        ).fetchone()
        if row is None:
            raise KeyError("unknown pilot session")
        return dict(row)

    def require_active_session(self, session_id: str, participant_id: str) -> dict[str, Any]:
        session = self.get_session(session_id, participant_id)
        if session["ended_at"]:
            raise ValueError("pilot session has ended")
        return session

    def record_event(
        self,
        *,
        event_type: str,
        session_id: str,
        participant_id: str,
        engine_version: str,
        payload: dict[str, Any] | None = None,
        input_id: str | None = None,
        duration_ms: float | None = None,
    ) -> dict[str, Any]:
        self.require_active_session(session_id, participant_id)
        with self._lock, self._connection:
            return self._insert_event(
                self._connection,
                event_type=event_type,
                session_id=session_id,
                participant_id=participant_id,
                engine_version=engine_version,
                payload=payload or {},
                input_id=input_id,
                duration_ms=duration_ms,
            )

    def _insert_event(
        self,
        connection: sqlite3.Connection,
        *,
        event_type: str,
        session_id: str,
        participant_id: str,
        engine_version: str,
        payload: dict[str, Any],
        input_id: str | None = None,
        duration_ms: float | None = None,
    ) -> dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported pilot event: {event_type}")
        event = {
            "id": str(uuid4()),
            "event_type": event_type,
            "session_id": session_id,
            "participant_id": participant_id,
            "input_id": input_id,
            "occurred_at": _now(),
            "engine_version": engine_version,
            "payload": {"event_schema_version": PILOT_EVENT_SCHEMA_VERSION, **payload},
            "duration_ms": duration_ms,
        }
        connection.execute(
            "INSERT INTO pilot_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                event["id"], event_type, session_id, participant_id, input_id,
                event["occurred_at"], engine_version,
                json.dumps(event["payload"], ensure_ascii=False, sort_keys=True),
                duration_ms,
            ),
        )
        connection.execute(
            "UPDATE pilot_sessions SET event_count = event_count + 1 WHERE id = ? AND participant_id = ?",
            (session_id, participant_id),
        )
        return event

    def end_session(self, session_id: str, participant_id: str, engine_version: str) -> dict[str, Any]:
        self.require_active_session(session_id, participant_id)
        ended_at = _now()
        with self._lock, self._connection:
            self._insert_event(
                self._connection,
                event_type="SESSION_ENDED",
                session_id=session_id,
                participant_id=participant_id,
                engine_version=engine_version,
                payload={},
            )
            self._connection.execute(
                "UPDATE pilot_sessions SET ended_at = ? WHERE id = ? AND participant_id = ?",
                (ended_at, session_id, participant_id),
            )
        return self.get_session(session_id, participant_id)

    def save_confirmed(
        self,
        record: dict[str, Any],
        *,
        participant_id: str | None = None,
        session_id: str | None = None,
        input_id: str | None = None,
    ) -> dict[str, Any]:
        if record.get("lifecycle_status") != "CONFIRMED" or not record.get("final_operation"):
            raise ValueError("only confirmed operations can be persisted")
        if bool(participant_id) != bool(session_id):
            raise ValueError("participant_id and session_id must be provided together")
        if participant_id and session_id:
            self.require_active_session(session_id, participant_id)
        proposal_id = record["proposal_id"]
        operation = record["final_operation"]
        confirmation = record.get("confirmation") or {}
        operation_id = str(uuid4())
        with self._lock, self._connection:
            existing = self._connection.execute(
                "SELECT id FROM operations WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
            if existing:
                return self.get_operation(existing["id"], participant_id=participant_id)
            self._connection.execute(
                """
                INSERT INTO operations (
                    id, proposal_id, operation_type, payload_json, original_text,
                    confirmed_at, participant_id, session_id, input_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    operation_id, proposal_id, operation["type"],
                    json.dumps(operation, ensure_ascii=False, sort_keys=True),
                    record.get("original_text"), confirmation["at"],
                    participant_id, session_id, input_id,
                ),
            )
            self._upsert_references(operation)
            self._apply_receivable(operation_id, operation, participant_id, session_id)
            for event in record.get("audit_events", []):
                self._connection.execute(
                    "INSERT INTO audit_events (proposal_id, occurred_at, action, details_json) VALUES (?, ?, ?, ?)",
                    (
                        proposal_id, event["at"], event["action"],
                        json.dumps(event.get("details", {}), ensure_ascii=False, sort_keys=True),
                    ),
                )
            if participant_id and session_id:
                self._insert_event(
                    self._connection,
                    event_type="OPERATION_CONFIRMED",
                    session_id=session_id,
                    participant_id=participant_id,
                    engine_version=record["engine_version"],
                    input_id=input_id,
                    payload={
                        "proposal_id": proposal_id,
                        "operation_id": operation_id,
                        "outcome_label": "USER_ACCEPTED_OPERATION",
                        "final_fields": operation,
                    },
                )
        return self.get_operation(operation_id, participant_id=participant_id)

    def _upsert_references(self, operation: dict[str, Any]) -> None:
        customer = operation.get("customer")
        if customer:
            self._connection.execute(
                "INSERT OR IGNORE INTO customer_references VALUES (?, ?)",
                (str(uuid4()), customer),
            )
        product = operation.get("product")
        if product:
            self._connection.execute(
                "INSERT OR IGNORE INTO product_references VALUES (?, ?, ?)",
                (str(uuid4()), product, operation.get("unit")),
            )

    def _apply_receivable(
        self,
        operation_id: str,
        operation: dict[str, Any],
        participant_id: str | None,
        session_id: str | None,
    ) -> None:
        if operation["type"] == "RECEIVABLE":
            amount = float(operation["amount"])
            self._connection.execute(
                """
                INSERT INTO receivables (
                    id, customer_label, original_amount, balance, status,
                    source_operation_id, participant_id, session_id
                ) VALUES (?, ?, ?, ?, 'OPEN', ?, ?, ?)
                """,
                (
                    str(uuid4()), operation["customer"], amount, amount,
                    operation_id, participant_id, session_id,
                ),
            )
        elif operation["type"] == "PAYMENT_RECEIVED":
            query = "SELECT id, balance FROM receivables WHERE lower(customer_label) = lower(?) AND status = 'OPEN'"
            params: list[Any] = [operation["customer"]]
            if participant_id:
                query += " AND participant_id = ?"
                params.append(participant_id)
            query += " ORDER BY rowid DESC LIMIT 1"
            row = self._connection.execute(query, params).fetchone()
            if row:
                balance = max(0.0, float(row["balance"]) - float(operation["amount"]))
                self._connection.execute(
                    "UPDATE receivables SET balance = ?, status = ? WHERE id = ?",
                    (balance, "PAID" if balance == 0 else "OPEN", row["id"]),
                )

    def get_operation(self, operation_id: str, participant_id: str | None = None) -> dict[str, Any]:
        query = "SELECT * FROM operations WHERE id = ?"
        params: list[Any] = [operation_id]
        if participant_id:
            query += " AND participant_id = ?"
            params.append(participant_id)
        row = self._connection.execute(query, params).fetchone()
        if row is None:
            raise KeyError(operation_id)
        return {
            "id": row["id"],
            "proposal_id": row["proposal_id"],
            "type": row["operation_type"],
            "operation": json.loads(row["payload_json"]),
            "original_text": row["original_text"],
            "confirmed_at": row["confirmed_at"],
            "participant_id": row["participant_id"],
            "session_id": row["session_id"],
            "input_id": row["input_id"],
        }

    def list_operations(self, limit: int = 50, participant_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT id FROM operations"
        params: list[Any] = []
        if participant_id:
            query += " WHERE participant_id = ?"
            params.append(participant_id)
        query += " ORDER BY rowid DESC LIMIT ?"
        params.append(limit)
        rows = self._connection.execute(query, params).fetchall()
        return [self.get_operation(row["id"], participant_id=participant_id) for row in rows]

    def list_receivables(self, participant_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM receivables"
        params: list[Any] = []
        if participant_id:
            query += " WHERE participant_id = ?"
            params.append(participant_id)
        query += " ORDER BY rowid DESC"
        return [dict(row) for row in self._connection.execute(query, params).fetchall()]

    def list_audit(self, operation_id: str, participant_id: str) -> list[dict[str, Any]]:
        operation = self.get_operation(operation_id, participant_id)
        rows = self._connection.execute(
            "SELECT occurred_at, action, details_json FROM audit_events WHERE proposal_id = ? ORDER BY id",
            (operation["proposal_id"],),
        ).fetchall()
        return [
            {"occurred_at": row["occurred_at"], "action": row["action"], "details": json.loads(row["details_json"])}
            for row in rows
        ]

    def save_feedback(self, session_id: str, participant_id: str, payload: dict[str, str]) -> dict[str, Any]:
        self.require_active_session(session_id, participant_id)
        record = {
            "id": str(uuid4()),
            "session_id": session_id,
            "participant_id": participant_id,
            "submitted_at": _now(),
            "payload": payload,
        }
        with self._connection:
            self._connection.execute(
                "INSERT INTO pilot_feedback VALUES (?, ?, ?, ?, ?)",
                (
                    record["id"], session_id, participant_id, record["submitted_at"],
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                ),
            )
        return record

    def annotate_input(
        self,
        *,
        input_id: str,
        participant_id: str,
        category: str,
        critical_financial_error: bool,
        note: str | None = None,
    ) -> dict[str, Any]:
        if not self._connection.execute(
            "SELECT 1 FROM pilot_events WHERE input_id = ? AND participant_id = ?",
            (input_id, participant_id),
        ).fetchone():
            raise KeyError("unknown input for participant")
        record = {
            "id": str(uuid4()), "input_id": input_id, "participant_id": participant_id,
            "category": category, "critical_financial_error": bool(critical_financial_error),
            "note": note, "annotated_at": _now(),
        }
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO pilot_annotations VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(input_id, category) DO UPDATE SET
                    critical_financial_error = excluded.critical_financial_error,
                    note = excluded.note, annotated_at = excluded.annotated_at
                """,
                (
                    record["id"], input_id, participant_id, category,
                    int(critical_financial_error), note, record["annotated_at"],
                ),
            )
        return record

    def metrics(self, participant_id: str | None = None) -> dict[str, Any]:
        query = "SELECT * FROM pilot_events"
        params: list[Any] = []
        if participant_id:
            query += " WHERE participant_id = ?"
            params.append(participant_id)
        query += " ORDER BY occurred_at"
        rows = self._connection.execute(query, params).fetchall()
        counts: dict[str, int] = defaultdict(int)
        by_input: dict[str, list[sqlite3.Row]] = defaultdict(list)
        sessions: set[str] = set()
        for row in rows:
            counts[row["event_type"]] += 1
            sessions.add(row["session_id"])
            if row["input_id"]:
                by_input[row["input_id"]].append(row)
        total_inputs = counts["TEXT_SUBMITTED"]
        terminal_times: list[float] = []
        confirmation_times: list[float] = []
        for events in by_input.values():
            submitted = next((row for row in events if row["event_type"] == "TEXT_SUBMITTED"), None)
            shown = next((row for row in events if row["event_type"] == "CONFIRMATION_SHOWN"), None)
            terminal = next(
                (row for row in events if row["event_type"] in {
                    "OPERATION_CONFIRMED", "OPERATION_REJECTED", "OPERATION_CANCELLED"
                }),
                None,
            )
            if submitted and terminal:
                terminal_times.append(
                    (datetime.fromisoformat(terminal["occurred_at"]) - datetime.fromisoformat(submitted["occurred_at"])).total_seconds()
                )
            if shown and terminal and terminal["event_type"] == "OPERATION_CONFIRMED":
                confirmation_times.append(
                    (datetime.fromisoformat(terminal["occurred_at"]) - datetime.fromisoformat(shown["occurred_at"])).total_seconds()
                )
        critical = self._connection.execute(
            "SELECT COUNT(*) FROM pilot_annotations WHERE critical_financial_error = 1"
            + (" AND participant_id = ?" if participant_id else ""),
            ([participant_id] if participant_id else []),
        ).fetchone()[0]
        rate = lambda n: (n / total_inputs) if total_inputs else None
        return {
            "definition_version": "pilot-metrics-v1",
            "total_inputs": total_inputs,
            "proposal_rate": rate(counts["CONFIRMATION_SHOWN"]),
            "confirmation_rate": rate(counts["OPERATION_CONFIRMED"]),
            "correction_rate": rate(counts["OPERATION_CORRECTED"]),
            "rejection_rate": rate(counts["OPERATION_REJECTED"]),
            "cancellation_rate": rate(counts["OPERATION_CANCELLED"]),
            "context_request_rate": rate(counts["CONTEXT_REQUESTED"]),
            "safe_abstention_rate": rate(
                sum(1 for events in by_input.values() if any(
                    row["event_type"] == "INTERPRETATION_CREATED"
                    and json.loads(row["payload_json"]).get("operation") is None
                    for row in events
                ))
            ),
            "critical_financial_errors": critical,
            "critical_financial_error_rate": (critical / total_inputs) if total_inputs else None,
            "successful_registration_rate": rate(counts["OPERATION_CONFIRMED"]),
            "median_time_to_register_seconds": median(terminal_times) if terminal_times else None,
            "p95_time_to_register_seconds": _percentile(terminal_times, 0.95),
            "median_confirmation_time_seconds": median(confirmation_times) if confirmation_times else None,
            "operations_per_session": (counts["OPERATION_CONFIRMED"] / len(sessions)) if sessions else None,
            "sessions": len(sessions),
        }

    def export_operational(self, participant_id: str) -> list[dict[str, Any]]:
        return self.list_operations(limit=100000, participant_id=participant_id)

    def export_real_development(self, participant_id: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            "SELECT * FROM pilot_events WHERE participant_id = ? AND input_id IS NOT NULL ORDER BY occurred_at",
            (participant_id,),
        ).fetchall()
        grouped: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in rows:
            grouped[row["input_id"]].append(row)
        exports: list[dict[str, Any]] = []
        for input_id, events in grouped.items():
            submitted = next((row for row in events if row["event_type"] == "TEXT_SUBMITTED"), None)
            interpreted = next((row for row in events if row["event_type"] == "INTERPRETATION_CREATED"), None)
            if not submitted or not interpreted:
                continue
            session = self.get_session(submitted["session_id"], participant_id)
            submitted_payload = json.loads(submitted["payload_json"])
            initial = json.loads(interpreted["payload_json"])
            operation_row = self._connection.execute(
                "SELECT payload_json FROM operations WHERE participant_id = ? AND input_id = ?",
                (participant_id, input_id),
            ).fetchone()
            corrections = [
                json.loads(row["payload_json"])
                for row in events if row["event_type"] == "OPERATION_CORRECTED"
            ]
            terminal = next(
                (row for row in reversed(events) if row["event_type"] in {
                    "OPERATION_CONFIRMED", "OPERATION_REJECTED", "OPERATION_CANCELLED"
                }),
                None,
            )
            exports.append({
                "record_id": input_id,
                "evidence_class": "REAL_DEVELOPMENT",
                "participant_id": participant_id,
                "session_id": submitted["session_id"],
                "original_text": submitted_payload["original_text"],
                "engine_version": session["engine_version"],
                "pilot_version": session["pilot_version"],
                "expected_or_final_accepted_operation": json.loads(operation_row["payload_json"]) if operation_row else None,
                "ground_truth_status": "USER_ACCEPTED_OPERATION" if operation_row else "NOT_ESTABLISHED",
                "initial_prediction": initial.get("predicted_operation"),
                "initial_fields": initial.get("fields", {}),
                "final_fields": json.loads(operation_row["payload_json"]) if operation_row else None,
                "context_used": initial.get("context_used", []),
                "corrections": corrections,
                "outcome": terminal["event_type"] if terminal else "OPEN",
                "safety_events": initial.get("safety_rules_triggered", []),
                "timestamps": {
                    "submitted_at": submitted["occurred_at"],
                    "interpreted_at": interpreted["occurred_at"],
                    "terminal_at": terminal["occurred_at"] if terminal else None,
                },
            })
        return exports

    def delete_participant(self, participant_id: str) -> dict[str, int]:
        operation_rows = self._connection.execute(
            "SELECT id, proposal_id FROM operations WHERE participant_id = ?", (participant_id,)
        ).fetchall()
        proposal_ids = [row["proposal_id"] for row in operation_rows]
        operation_ids = [row["id"] for row in operation_rows]
        counts = {
            "operations": len(operation_ids),
            "sessions": self._connection.execute(
                "SELECT COUNT(*) FROM pilot_sessions WHERE participant_id = ?", (participant_id,)
            ).fetchone()[0],
            "events": self._connection.execute(
                "SELECT COUNT(*) FROM pilot_events WHERE participant_id = ?", (participant_id,)
            ).fetchone()[0],
        }
        with self._lock, self._connection:
            if operation_ids:
                placeholders = ",".join("?" for _ in operation_ids)
                self._connection.execute(
                    f"DELETE FROM receivables WHERE source_operation_id IN ({placeholders}) OR participant_id = ?",
                    [*operation_ids, participant_id],
                )
            else:
                self._connection.execute("DELETE FROM receivables WHERE participant_id = ?", (participant_id,))
            if proposal_ids:
                placeholders = ",".join("?" for _ in proposal_ids)
                self._connection.execute(
                    f"DELETE FROM audit_events WHERE proposal_id IN ({placeholders})", proposal_ids
                )
            self._connection.execute("DELETE FROM operations WHERE participant_id = ?", (participant_id,))
            self._connection.execute("DELETE FROM access_sessions WHERE participant_id = ?", (participant_id,))
            self._connection.execute("DELETE FROM participants WHERE id = ?", (participant_id,))
        return counts

    def counts(self) -> dict[str, int]:
        return {
            "participants": self._connection.execute("SELECT COUNT(*) FROM participants").fetchone()[0],
            "real_development_records": self._connection.execute(
                "SELECT COUNT(*) FROM pilot_events WHERE event_type = 'TEXT_SUBMITTED'"
            ).fetchone()[0],
            "critical_errors": self._connection.execute(
                "SELECT COUNT(*) FROM pilot_annotations WHERE critical_financial_error = 1"
            ).fetchone()[0],
        }

    def close(self) -> None:
        if not self._closed:
            self._connection.close()
            self._closed = True
