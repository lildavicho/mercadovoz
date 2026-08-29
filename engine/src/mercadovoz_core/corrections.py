from __future__ import annotations

import copy
import re
from decimal import Decimal
from typing import Any

from mercadovoz.corrections import apply_correction
from mercadovoz.models import json_number, missing_fields, validate_operation
from mercadovoz.parser import confirmation_prompt, normalize_text


NUMBER = r"\d+(?:[.,]\d+)?"


def _result(operation: dict[str, Any], changed: list[str]) -> dict[str, Any]:
    if operation.get("quantity") is not None and operation.get("unit_price") is not None:
        operation["total"] = json_number(
            Decimal(str(operation["quantity"])) * Decimal(str(operation["unit_price"]))
        )
        if "total" not in changed:
            changed.append("total")
    missing = missing_fields(operation)
    errors = validate_operation(operation)
    status = "COMPLETE" if not missing and not errors else "NEEDS_CONFIRMATION"
    return {
        "status": status,
        "operation": operation,
        "missing_fields": missing,
        "question": confirmation_prompt(operation) if status == "COMPLETE" else "La operación aún necesita datos.",
        "warnings": [f"corrected:{field}" for field in changed] + errors,
    }


def apply_controlled_correction(result: dict[str, Any], correction_text: str) -> dict[str, Any]:
    operation = copy.deepcopy(result.get("operation"))
    if not operation:
        return apply_correction(result, correction_text)
    text = normalize_text(correction_text)

    replacement = re.fullmatch(r"no era (?P<old>[a-zñ ]+),? era (?P<new>[a-zñ ]+)", text)
    if replacement and operation.get("customer"):
        old = replacement.group("old").strip()
        current = normalize_text(str(operation["customer"]))
        if old != current:
            return {
                "status": "NEEDS_CONFIRMATION",
                "operation": operation,
                "missing_fields": missing_fields(operation),
                "question": "La persona indicada no coincide con la operación pendiente.",
                "warnings": ["correction_target_mismatch"],
            }
        operation["customer"] = replacement.group("new").strip().title()
        return _result(operation, ["customer"])

    product = re.fullmatch(r"era (?P<product>[a-zñ][a-zñ ]*)", text)
    if product and "product" in operation:
        operation["product"] = product.group("product").strip()
        return _result(operation, ["product"])

    amount = re.fullmatch(r"eran (?P<amount>\d+(?:[.,]\d+)?) dolares?", text)
    if amount and "amount" in operation:
        operation["amount"] = json_number(Decimal(amount.group("amount").replace(",", ".")))
        return _result(operation, ["amount"])

    return apply_correction(result, correction_text)
