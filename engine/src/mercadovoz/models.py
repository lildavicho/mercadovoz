from __future__ import annotations

from decimal import Decimal
from typing import Any

STATUSES = {"COMPLETE", "NEEDS_CONFIRMATION", "UNRECOGNIZED"}
CORE_OPERATION_TYPES = {
    "SALE",
    "EXPENSE",
    "RECEIVABLE",
    "PAYMENT_RECEIVED",
}
EXPLORATORY_OPERATION_TYPES = {"PURCHASE", "STOCK_ADJUSTMENT"}
OPERATION_TYPES = CORE_OPERATION_TYPES | EXPLORATORY_OPERATION_TYPES

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "SALE": ("product", "quantity", "unit", "total"),
    "PURCHASE": ("product", "quantity", "unit", "unit_price", "total"),
    "EXPENSE": ("category", "amount"),
    "RECEIVABLE": ("customer", "amount"),
    "PAYMENT_RECEIVED": ("customer", "amount"),
    "STOCK_ADJUSTMENT": ("product", "quantity", "unit", "mode"),
}

NUMERIC_FIELDS = {"quantity", "unit_price", "total", "amount"}


def json_number(value: Decimal | float | int) -> int | float:
    number = Decimal(str(value))
    if number == number.to_integral_value():
        return int(number)
    return float(number.quantize(Decimal("0.01")))


def missing_fields(operation: dict[str, Any]) -> list[str]:
    operation_type = operation.get("type")
    required = REQUIRED_FIELDS.get(operation_type, ())
    return [field for field in required if operation.get(field) in (None, "")]


def validate_operation(operation: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    operation_type = operation.get("type")
    if operation_type not in OPERATION_TYPES:
        return ["unsupported_operation_type"]

    errors.extend(f"missing:{field}" for field in missing_fields(operation))
    for field in NUMERIC_FIELDS:
        if field in operation and operation[field] is not None:
            try:
                if Decimal(str(operation[field])) <= 0:
                    errors.append(f"non_positive:{field}")
            except Exception:
                errors.append(f"not_numeric:{field}")

    if operation_type in {"SALE", "PURCHASE"}:
        quantity = operation.get("quantity")
        unit_price = operation.get("unit_price")
        total = operation.get("total")
        if quantity is not None and unit_price is not None and total is not None:
            expected = Decimal(str(quantity)) * Decimal(str(unit_price))
            if abs(expected - Decimal(str(total))) > Decimal("0.01"):
                errors.append("inconsistent_total")
    return errors
