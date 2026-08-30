from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from threading import RLock
from typing import Any
from uuid import uuid4

from mercadovoz.numbers import strip_accents
from mercadovoz_core.storage import SQLiteLedger


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _minor(value: Any) -> int:
    amount = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(amount * 100)


def _major(value: int) -> float | int:
    amount = Decimal(value) / Decimal(100)
    return int(amount) if amount == amount.to_integral_value() else float(amount)


def _customer_key(value: Any) -> str:
    return " ".join(strip_accents(str(value)).casefold().split())


class BatchLedger:
    """Durable batch persistence layered on the legacy SQLite store."""

    def __init__(self, ledger: SQLiteLedger) -> None:
        self.ledger = ledger
        self._connection = ledger._connection
        self._lock: RLock = ledger._lock

    def register(
        self,
        batch: dict[str, Any],
        *,
        participant_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        self.ledger.require_active_session(session_id, participant_id)
        with self._lock, self._connection:
            existing = self._connection.execute(
                "SELECT id FROM batch_inputs WHERE id = ? AND participant_id = ?",
                (batch["batch_id"], participant_id),
            ).fetchone()
            if existing:
                return self.get_batch(batch["batch_id"], participant_id)
            created_at = _now()
            self._connection.execute(
                """
                INSERT INTO batch_inputs (
                    id, participant_id, session_id, input_mode, source_text,
                    engine_version, schema_version, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch["batch_id"], participant_id, session_id, batch["input_mode"],
                    batch["source_text"], batch["engine_version"], batch["schema_version"],
                    batch["status"], created_at,
                ),
            )
            self._audit(
                batch["batch_id"], participant_id, "BATCH_SUBMITTED",
                {"input_mode": batch["input_mode"]},
            )
            self._audit(
                batch["batch_id"], participant_id, "BATCH_SEGMENTED",
                {"segment_count": len(batch["segments"]), "segmenter_version": batch["segmenter_version"]},
            )
            for group in batch.get("groups", []):
                self._connection.execute(
                    "INSERT INTO transaction_groups VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        group["group_id"], batch["batch_id"], group["type"],
                        group.get("customer"), json.dumps(group, ensure_ascii=False, sort_keys=True),
                        created_at,
                    ),
                )
            for ordinal, item in enumerate(batch["segments"], start=1):
                span = item["source_span"]
                if batch["source_text"][span["start"] : span["end"]] != item["source_text"]:
                    raise ValueError("source span does not match source text")
                self._connection.execute(
                    """
                    INSERT INTO batch_items (
                        id, batch_id, ordinal, source_start, source_end, source_text,
                        interpretation_state, confirmable, transaction_group_id,
                        interpretation_json, lifecycle_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PROPOSED')
                    """,
                    (
                        item["segment_id"], batch["batch_id"], ordinal,
                        span["start"], span["end"], item["source_text"], item["state"],
                        int(item["confirmable"]), item.get("transaction_group_id"),
                        json.dumps(item, ensure_ascii=False, sort_keys=True),
                    ),
                )
                self._audit(
                    batch["batch_id"], participant_id, "ITEM_INTERPRETED",
                    {"state": item["state"], "confirmable": item["confirmable"]},
                    item_id=item["segment_id"],
                )
                if item["state"] in {"NEEDS_CONTEXT", "NEEDS_CONFIRMATION", "AMBIGUOUS"}:
                    self._audit(
                        batch["batch_id"], participant_id, "ITEM_CONTEXT_REQUESTED",
                        {"state": item["state"]}, item_id=item["segment_id"],
                    )
        return self.get_batch(batch["batch_id"], participant_id)

    def confirm(
        self,
        batch: dict[str, Any],
        *,
        item_ids: list[str],
        idempotency_key: str,
        participant_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        if len(idempotency_key.strip()) < 8:
            raise ValueError("idempotency key must contain at least 8 characters")
        if not item_ids or len(item_ids) != len(set(item_ids)):
            raise ValueError("item_ids must be a non-empty unique list")
        request_hash = hashlib.sha256(json.dumps({
            "batch_id": batch["batch_id"], "item_ids": sorted(item_ids),
        }, sort_keys=True).encode("utf-8")).hexdigest()

        with self._lock:
            existing = self._connection.execute(
                """
                SELECT id, request_hash FROM batch_confirmations
                WHERE participant_id = ? AND idempotency_key = ?
                """,
                (participant_id, idempotency_key),
            ).fetchone()
            if existing:
                if existing["request_hash"] != request_hash:
                    raise ValueError("idempotency key was already used for a different request")
                return self._confirmation_result(existing["id"], participant_id)

            self.ledger.require_active_session(session_id, participant_id)
            registered = self.get_batch(batch["batch_id"], participant_id)
            if registered["session_id"] != session_id:
                raise ValueError("batch does not belong to this session")
            by_id = {item["segment_id"]: item for item in batch["segments"]}
            selected: list[dict[str, Any]] = []
            for item_id in item_ids:
                item = by_id.get(item_id)
                if not item:
                    raise ValueError("unknown batch item")
                if not item.get("confirmable") or item.get("state") != "COMPLETE":
                    raise ValueError("batch item is not confirmable")
                selected.append(item)
            self._validate_dependencies(selected, set(item_ids))
            allocation_plan = self._plan_allocations(selected, participant_id)

            confirmation_id = str(uuid4())
            confirmed_at = _now()
            status = "CONFIRMED" if len(item_ids) == len(batch["segments"]) else "PARTIALLY_CONFIRMED"
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                self._connection.execute(
                    "INSERT INTO batch_confirmations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        confirmation_id, batch["batch_id"], participant_id, session_id,
                        idempotency_key, request_hash, status, confirmed_at,
                    ),
                )
                operations: list[dict[str, Any]] = []
                for item in sorted(selected, key=lambda value: value["sequence"]):
                    operation_id = self._insert_operation(
                        batch, item, participant_id, session_id, confirmed_at
                    )
                    operation = item["operation"]
                    if operation["type"] == "RECEIVABLE":
                        self._create_receivable(operation_id, operation, participant_id, session_id, confirmed_at)
                    elif operation["type"] == "PAYMENT_RECEIVED" and operation.get("settlement_role") != "PAYMENT_AT_SALE":
                        self._apply_payment(
                            operation_id, operation, allocation_plan[item["segment_id"]], confirmed_at
                        )
                    self._insert_line_items(operation_id, operation)
                    self._connection.execute(
                        "INSERT INTO batch_confirmation_items VALUES (?, ?, ?)",
                        (confirmation_id, item["segment_id"], operation_id),
                    )
                    self._connection.execute(
                        "UPDATE batch_items SET lifecycle_status = 'CONFIRMED' WHERE id = ?",
                        (item["segment_id"],),
                    )
                    self._audit(
                        batch["batch_id"], participant_id, "ITEM_CONFIRMED",
                        {"operation_id": operation_id}, item_id=item["segment_id"],
                    )
                    operations.append(self.ledger.get_operation(operation_id, participant_id))
                self._audit(
                    batch["batch_id"], participant_id,
                    "BATCH_CONFIRMED" if status == "CONFIRMED" else "BATCH_PARTIALLY_CONFIRMED",
                    {"confirmation_id": confirmation_id, "item_count": len(item_ids)},
                )
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise
        return self._confirmation_result(confirmation_id, participant_id)

    def result_for_key(self, participant_id: str, idempotency_key: str) -> dict[str, Any] | None:
        row = self._connection.execute(
            "SELECT id FROM batch_confirmations WHERE participant_id = ? AND idempotency_key = ?",
            (participant_id, idempotency_key),
        ).fetchone()
        return self._confirmation_result(row["id"], participant_id) if row else None

    def get_batch(self, batch_id: str, participant_id: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT * FROM batch_inputs WHERE id = ? AND participant_id = ?",
            (batch_id, participant_id),
        ).fetchone()
        if row is None:
            raise KeyError("unknown batch")
        return dict(row)

    def list_groups(self, participant_id: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            """
            SELECT g.payload_json FROM transaction_groups g
            JOIN batch_inputs b ON b.id = g.batch_id
            WHERE b.participant_id = ? ORDER BY g.rowid DESC
            """,
            (participant_id,),
        ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def update_item(
        self,
        batch_id: str,
        item: dict[str, Any],
        participant_id: str,
        *,
        action: str = "ITEM_CORRECTED",
    ) -> None:
        if action not in {"ITEM_CORRECTED", "ITEM_REJECTED"}:
            raise ValueError("unsupported item audit action")
        with self._lock, self._connection:
            owner = self._connection.execute(
                "SELECT 1 FROM batch_inputs WHERE id = ? AND participant_id = ?",
                (batch_id, participant_id),
            ).fetchone()
            if not owner:
                raise KeyError("unknown batch")
            updated = self._connection.execute(
                """
                UPDATE batch_items SET interpretation_state = ?, confirmable = ?,
                    interpretation_json = ?, lifecycle_status = ?
                WHERE id = ? AND batch_id = ?
                """,
                (
                    item["state"], int(item["confirmable"]),
                    json.dumps(item, ensure_ascii=False, sort_keys=True),
                    item.get("lifecycle_status", "PROPOSED"), item["segment_id"], batch_id,
                ),
            )
            if updated.rowcount != 1:
                raise KeyError("unknown batch item")
            self._audit(
                batch_id, participant_id, action,
                {"state": item["state"], "confirmable": item["confirmable"]},
                item_id=item["segment_id"],
            )

    @staticmethod
    def _validate_dependencies(selected: list[dict[str, Any]], selected_ids: set[str]) -> None:
        for item in selected:
            missing = set(item.get("depends_on", [])) - selected_ids
            if missing:
                raise ValueError("dependent item requires its source item in the same confirmation")

    def _plan_allocations(
        self, selected: list[dict[str, Any]], participant_id: str
    ) -> dict[str, dict[str, Any]]:
        plan: dict[str, dict[str, Any]] = {}
        for item in selected:
            operation = item["operation"]
            if operation["type"] != "PAYMENT_RECEIVED" or operation.get("settlement_role") == "PAYMENT_AT_SALE":
                continue
            params: list[Any] = [participant_id]
            query = "SELECT id, customer_label, balance FROM receivables WHERE participant_id = ? AND status = 'OPEN'"
            if operation.get("receivable_id"):
                query += " AND id = ?"
                params.append(operation["receivable_id"])
            rows = self._connection.execute(query, params).fetchall()
            if not operation.get("receivable_id"):
                customer_key = _customer_key(operation["customer"])
                rows = [row for row in rows if _customer_key(row["customer_label"]) == customer_key]
            if not rows:
                raise ValueError("payment requires an open receivable")
            if len(rows) > 1:
                raise ValueError("payment requires explicit receivable selection")
            row = rows[0]
            if _customer_key(row["customer_label"]) != _customer_key(operation["customer"]):
                raise ValueError("payment customer does not match receivable")
            payment_minor = _minor(operation["amount"])
            balance_minor = _minor(row["balance"])
            if payment_minor > balance_minor:
                raise ValueError("payment exceeds outstanding balance")
            plan[item["segment_id"]] = {
                "receivable_id": row["id"], "payment_minor": payment_minor,
                "previous_minor": balance_minor, "new_minor": balance_minor - payment_minor,
            }
        return plan

    def _insert_operation(
        self,
        batch: dict[str, Any],
        item: dict[str, Any],
        participant_id: str,
        session_id: str,
        confirmed_at: str,
    ) -> str:
        operation_id = str(uuid4())
        proposal_id = f"batch:{batch['batch_id']}:{item['segment_id']}"
        self._connection.execute(
            """
            INSERT INTO operations (
                id, proposal_id, operation_type, payload_json, original_text,
                confirmed_at, participant_id, session_id, input_id,
                batch_id, segment_id, transaction_group_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                operation_id, proposal_id, item["operation"]["type"],
                json.dumps(item["operation"], ensure_ascii=False, sort_keys=True),
                item["source_text"], confirmed_at, participant_id, session_id,
                batch["batch_id"], batch["batch_id"], item["segment_id"],
                item.get("transaction_group_id"),
            ),
        )
        self._connection.execute(
            "INSERT INTO audit_events (proposal_id, occurred_at, action, details_json) VALUES (?, ?, ?, ?)",
            (
                proposal_id, confirmed_at, "BATCH_CONFIRMED",
                json.dumps({
                    "batch_id": batch["batch_id"], "segment_id": item["segment_id"],
                    "source_span": item["source_span"],
                    "field_provenance": item.get("field_provenance", {}),
                }, ensure_ascii=False, sort_keys=True),
            ),
        )
        return operation_id

    def _create_receivable(
        self,
        operation_id: str,
        operation: dict[str, Any],
        participant_id: str,
        session_id: str,
        created_at: str,
    ) -> str:
        amount_minor = _minor(operation["amount"])
        receivable_id = str(uuid4())
        self._connection.execute(
            """
            INSERT INTO receivables (
                id, customer_label, original_amount, balance, status,
                source_operation_id, participant_id, session_id, created_at, closed_at
            ) VALUES (?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, NULL)
            """,
            (
                receivable_id, operation["customer"], _major(amount_minor), _major(amount_minor),
                operation_id, participant_id, session_id, created_at,
            ),
        )
        self._connection.execute(
            "INSERT INTO receivable_movements VALUES (?, ?, ?, 'CREATED', ?, 0, ?, ?)",
            (str(uuid4()), receivable_id, operation_id, amount_minor, amount_minor, created_at),
        )
        return receivable_id

    def _apply_payment(
        self,
        operation_id: str,
        operation: dict[str, Any],
        allocation: dict[str, Any],
        created_at: str,
    ) -> None:
        new_minor = allocation["new_minor"]
        self._connection.execute(
            "UPDATE receivables SET balance = ?, status = ?, closed_at = ? WHERE id = ?",
            (
                _major(new_minor), "PAID" if new_minor == 0 else "OPEN",
                created_at if new_minor == 0 else None, allocation["receivable_id"],
            ),
        )
        values = (
            str(uuid4()), operation_id, allocation["receivable_id"],
            allocation["payment_minor"], allocation["previous_minor"], new_minor, created_at,
        )
        self._connection.execute("INSERT INTO payment_allocations VALUES (?, ?, ?, ?, ?, ?, ?)", values)
        self._connection.execute(
            "INSERT INTO receivable_movements VALUES (?, ?, ?, 'PAYMENT', ?, ?, ?, ?)",
            (
                str(uuid4()), allocation["receivable_id"], operation_id,
                allocation["payment_minor"], allocation["previous_minor"], new_minor, created_at,
            ),
        )

    def _insert_line_items(self, operation_id: str, operation: dict[str, Any]) -> None:
        for ordinal, item in enumerate(operation.get("line_items", []), start=1):
            self._connection.execute(
                "INSERT INTO operation_line_items VALUES (?, ?, ?, ?)",
                (item.get("line_item_id", str(uuid4())), operation_id, ordinal,
                 json.dumps(item, ensure_ascii=False, sort_keys=True)),
            )

    def _confirmation_result(self, confirmation_id: str, participant_id: str) -> dict[str, Any]:
        confirmation = self._connection.execute(
            "SELECT * FROM batch_confirmations WHERE id = ? AND participant_id = ?",
            (confirmation_id, participant_id),
        ).fetchone()
        if confirmation is None:
            raise KeyError("unknown batch confirmation")
        rows = self._connection.execute(
            "SELECT operation_id FROM batch_confirmation_items WHERE confirmation_id = ? ORDER BY rowid",
            (confirmation_id,),
        ).fetchall()
        return {
            "confirmation_id": confirmation_id,
            "batch_id": confirmation["batch_id"],
            "status": confirmation["status"],
            "confirmed_at": confirmation["confirmed_at"],
            "operations": [
                self.ledger.get_operation(row["operation_id"], participant_id) for row in rows
            ],
        }

    def _audit(
        self,
        batch_id: str,
        participant_id: str,
        action: str,
        details: dict[str, Any],
        *,
        item_id: str | None = None,
    ) -> None:
        self._connection.execute(
            "INSERT INTO batch_audit_events VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid4()), batch_id, item_id, participant_id, _now(), action,
                json.dumps(details, ensure_ascii=False, sort_keys=True),
            ),
        )
