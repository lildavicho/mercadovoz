from __future__ import annotations

import re
from copy import deepcopy
from decimal import Decimal
from typing import Any
from uuid import uuid4

from mercadovoz.models import json_number, missing_fields, validate_operation
from mercadovoz.numbers import to_decimal
from mercadovoz.parser import normalize_text

from .context import ContextSession, ContextValue, utc_now
from .parsers import CompositeParser, Parser
from .safety import inspect_safety
from .versioning import CONTEXT_VERSION, ENGINE_VERSION, PARSER_VERSION, SCHEMA_VERSION


INTERPRETATION_STATUSES = {
    "COMPLETE",
    "NEEDS_CONFIRMATION",
    "NEEDS_CONTEXT",
    "AMBIGUOUS",
    "COMPOUND_OPERATION",
    "OUT_OF_SCOPE",
    "UNSAFE",
    "UNRECOGNIZED",
}


def _context_record(key: str, entry: ContextValue) -> dict[str, Any]:
    snapshot = entry.snapshot()
    return {"key": key, **snapshot}


class MercadoVozEngine:
    """Rules v0 wrapped by explicit context and fail-safe interpretation rules."""

    parser_version = PARSER_VERSION

    def __init__(self, parser: Parser | None = None) -> None:
        self.parser = parser or CompositeParser()

    def interpret(self, text: str, context: ContextSession | None = None) -> dict[str, Any]:
        original = text.strip()
        normalized = normalize_text(original)
        interpreted_at = utc_now().isoformat()
        safety = inspect_safety(original)
        if safety:
            return {
                "interpretation_id": str(uuid4()),
                "interpreted_at": interpreted_at,
                "original_text": original,
                "normalized_text": normalized,
                "parser_version": self.parser_version,
                "engine_version": ENGINE_VERSION,
                "schema_version": SCHEMA_VERSION,
                "context_version": CONTEXT_VERSION,
                "status": safety.status,
                "lifecycle_status": None,
                "context_used": [],
                "fields_extracted": {},
                "computed_fields": {},
                "missing_fields": [],
                "warnings": [safety.warning],
                "safety_rules_triggered": [safety.warning],
                "question": safety.question,
                "operation": None,
            }

        baseline = self.parser.parse(original)
        operation = deepcopy(baseline.get("operation"))
        used: list[dict[str, Any]] = []
        computed: dict[str, Any] = dict(baseline.get("computed_fields", {}))
        if operation and context:
            self._apply_explicit_context(operation, original, context, used, computed)

        if operation:
            missing = missing_fields(operation)
            errors = validate_operation(operation)
            warnings = list(dict.fromkeys([*baseline.get("warnings", []), *errors]))
            if not missing and not errors:
                status = "COMPLETE"
                question = baseline.get("question") or "Confirme la operación propuesta."
            elif self._is_context_gap(operation, missing):
                status = "NEEDS_CONTEXT"
                question = "Seleccione el contexto faltante antes de proponer la operación."
            else:
                status = "NEEDS_CONFIRMATION"
                question = baseline.get("question") or "Complete o corrija la operación."
        else:
            missing = baseline.get("missing_fields", [])
            warnings = baseline.get("warnings", [])
            status = baseline.get("status", "UNRECOGNIZED")
            question = baseline.get("question")

        return {
            "interpretation_id": str(uuid4()),
            "interpreted_at": interpreted_at,
            "original_text": original,
            "normalized_text": normalized,
            "parser_version": self.parser_version,
            "engine_version": ENGINE_VERSION,
            "schema_version": SCHEMA_VERSION,
            "context_version": CONTEXT_VERSION,
            "status": status,
            "lifecycle_status": "PROPOSED" if operation else None,
            "context_used": used,
            "fields_extracted": deepcopy(operation) if operation else {},
            "computed_fields": computed,
            "missing_fields": missing,
            "warnings": warnings,
            "safety_rules_triggered": [],
            "question": question,
            "operation": operation,
        }

    def _apply_explicit_context(
        self,
        operation: dict[str, Any],
        original_text: str,
        context: ContextSession,
        used: list[dict[str, Any]],
        computed: dict[str, Any],
    ) -> None:
        def use(key: str) -> ContextValue | None:
            entry = context.get(key)
            if entry:
                used.append(_context_record(key, entry))
            return entry

        operation_type = operation.get("type")
        if operation_type in {"SALE", "PURCHASE"} and not operation.get("product"):
            entry = use("active_product")
            if entry:
                operation["product"] = entry.value
        if operation_type == "STOCK_ADJUSTMENT" and not operation.get("product"):
            entry = use("active_stock_item")
            if entry:
                value = entry.value
                operation["product"] = value.get("product") if isinstance(value, dict) else value
                if isinstance(value, dict) and not operation.get("unit"):
                    operation["unit"] = value.get("unit")

        if operation_type in {"RECEIVABLE", "PAYMENT_RECEIVED"} and not operation.get("customer"):
            receivable = use("active_receivable") if operation_type == "PAYMENT_RECEIVED" else None
            if receivable and isinstance(receivable.value, dict):
                operation["customer"] = receivable.value.get("customer")
            if not operation.get("customer"):
                customer = use("active_customer")
                if customer:
                    operation["customer"] = customer.value

        if operation_type == "PAYMENT_RECEIVED" and not operation.get("amount"):
            normalized = normalize_text(original_text)
            match = re.search(r"\b(?:me pago|abono|me dejo)\s+\$?\s*(\d+(?:[.,]\d+)?)", normalized)
            if match:
                value = to_decimal(match.group(1))
                if value is not None:
                    operation["amount"] = json_number(value)

        if operation_type == "PAYMENT_RECEIVED" and operation.get("amount") is not None:
            receivable = context.get("active_receivable")
            if receivable and isinstance(receivable.value, dict) and receivable.value.get("balance") is not None:
                if not any(item["key"] == "active_receivable" for item in used):
                    used.append(_context_record("active_receivable", receivable))
                balance = Decimal(str(receivable.value["balance"]))
                amount = Decimal(str(operation["amount"]))
                computed["remaining_balance"] = json_number(max(Decimal("0"), balance - amount))
                if receivable.value.get("receivable_id"):
                    computed["receivable_id"] = receivable.value["receivable_id"]

    @staticmethod
    def _is_context_gap(operation: dict[str, Any], missing: list[str]) -> bool:
        operation_type = operation.get("type")
        context_fields = {
            "SALE": {"product"},
            "PURCHASE": {"product"},
            "RECEIVABLE": {"customer"},
            "PAYMENT_RECEIVED": {"customer"},
            "STOCK_ADJUSTMENT": {"product", "unit"},
        }
        return bool(set(missing) & context_fields.get(operation_type, set()))
