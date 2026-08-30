from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from .validation import validate_batch_operation


ALLOWED_CORRECTION_FIELDS = {
    "type", "amount", "quantity", "product", "customer", "category",
    "unit", "unit_price", "total", "receivable_id",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BatchWorkflow:
    """In-memory review state; durable confirmation remains in BatchLedger."""

    def __init__(self) -> None:
        self._batches: dict[str, dict[str, Any]] = {}

    def propose(self, batch: dict[str, Any]) -> dict[str, Any]:
        self._batches[batch["batch_id"]] = deepcopy(batch)
        return deepcopy(batch)

    def get(self, batch_id: str) -> dict[str, Any]:
        try:
            return deepcopy(self._batches[batch_id])
        except KeyError as exc:
            raise KeyError("unknown batch proposal") from exc

    def correct_item(
        self, batch_id: str, item_id: str, changes: dict[str, Any]
    ) -> dict[str, Any]:
        if not changes or set(changes) - ALLOWED_CORRECTION_FIELDS:
            raise ValueError("unsupported or empty item correction")
        batch, item = self._mutable_item(batch_id, item_id)
        if item.get("lifecycle_status") in {"CONFIRMED", "REJECTED", "CANCELLED"}:
            raise ValueError("terminal batch item cannot be corrected")
        operation = deepcopy(item.get("operation") or {})
        before = deepcopy(operation)
        operation.update(changes)
        if operation.get("type") == "SALE" and not operation.get("line_items"):
            if "total" not in changes and operation.get("quantity") is not None and operation.get("unit_price") is not None:
                operation["total"] = float(
                    Decimal(str(operation["quantity"])) * Decimal(str(operation["unit_price"]))
                )
        errors = validate_batch_operation(operation)
        item["operation"] = operation
        item["fields_extracted"] = deepcopy(operation)
        item["state"] = "COMPLETE" if not errors else "NEEDS_CONFIRMATION"
        item["confirmable"] = not errors
        item["warnings"] = errors
        item["lifecycle_status"] = "CORRECTED"
        correction = {
            "at": _now(),
            "changes": [
                {"field": field, "old_value": before.get(field), "new_value": operation.get(field)}
                for field in sorted(changes)
                if before.get(field) != operation.get(field)
            ],
        }
        item.setdefault("human_corrections", []).append(correction)
        for field in changes:
            item.setdefault("field_provenance", {})[field] = {
                "source": "HUMAN_CORRECTION", "derived": False,
            }
        self._refresh(batch)
        return deepcopy(item)

    def terminate_item(self, batch_id: str, item_id: str, status: str) -> dict[str, Any]:
        if status not in {"REJECTED", "CANCELLED"}:
            raise ValueError("unsupported terminal status")
        batch, item = self._mutable_item(batch_id, item_id)
        if item.get("lifecycle_status") == "CONFIRMED":
            raise ValueError("confirmed batch item cannot be terminated")
        item["lifecycle_status"] = status
        item["confirmable"] = False
        item["state"] = status
        self._refresh(batch)
        return deepcopy(item)

    def _mutable_item(self, batch_id: str, item_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        try:
            batch = self._batches[batch_id]
        except KeyError as exc:
            raise KeyError("unknown batch proposal") from exc
        item = next((entry for entry in batch["segments"] if entry["segment_id"] == item_id), None)
        if item is None:
            raise KeyError("unknown batch item")
        return batch, item

    @staticmethod
    def _refresh(batch: dict[str, Any]) -> None:
        available = [
            item for item in batch["segments"]
            if item.get("lifecycle_status") not in {"REJECTED", "CANCELLED"}
        ]
        confirmable = [item for item in available if item.get("confirmable")]
        batch["confirmable_item_ids"] = [item["segment_id"] for item in confirmable]
        if available and len(confirmable) == len(available):
            batch["status"] = "READY"
        elif confirmable:
            batch["status"] = "PARTIALLY_READY"
        elif available:
            batch["status"] = "NEEDS_REVIEW"
        else:
            batch["status"] = "BLOCKED"
