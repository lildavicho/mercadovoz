from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


CORE_TYPES = {"SALE", "EXPENSE", "RECEIVABLE", "PAYMENT_RECEIVED"}


def _positive(value: Any) -> bool:
    try:
        return Decimal(str(value)) > 0
    except (InvalidOperation, TypeError, ValueError):
        return False


def validate_batch_operation(operation: dict[str, Any]) -> list[str]:
    operation_type = operation.get("type")
    if operation_type not in CORE_TYPES:
        return ["unsupported_operation_type"]
    errors: list[str] = []
    if operation_type == "SALE":
        line_items = operation.get("line_items")
        if line_items:
            if not isinstance(line_items, list):
                return ["invalid_line_items"]
            expected = Decimal("0")
            for item in line_items:
                for field in ("product", "quantity", "unit", "unit_price", "total"):
                    if item.get(field) in (None, ""):
                        errors.append(f"missing:line_items.{field}")
                if not _positive(item.get("quantity")) or not _positive(item.get("unit_price")):
                    errors.append("invalid_line_item_amount")
                else:
                    expected += Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"]))
            if not _positive(operation.get("total")):
                errors.append("missing:total")
            elif abs(expected - Decimal(str(operation["total"]))) > Decimal("0.01"):
                errors.append("inconsistent_total")
        else:
            for field in ("product", "quantity", "unit", "total"):
                if operation.get(field) in (None, ""):
                    errors.append(f"missing:{field}")
            if operation.get("unit_price") is not None:
                if not _positive(operation["unit_price"]):
                    errors.append("invalid:unit_price")
                elif operation.get("quantity") is not None and operation.get("total") is not None:
                    expected = Decimal(str(operation["quantity"])) * Decimal(str(operation["unit_price"]))
                    if abs(expected - Decimal(str(operation["total"]))) > Decimal("0.01"):
                        errors.append("inconsistent_total")
            for field in ("quantity", "total"):
                if operation.get(field) is not None and not _positive(operation[field]):
                    errors.append(f"invalid:{field}")
    elif operation_type == "EXPENSE":
        if not operation.get("category"):
            errors.append("missing:category")
        if not _positive(operation.get("amount")):
            errors.append("invalid:amount")
    else:
        if not operation.get("customer"):
            errors.append("missing:customer")
        if not _positive(operation.get("amount")):
            errors.append("invalid:amount")
    return list(dict.fromkeys(errors))
