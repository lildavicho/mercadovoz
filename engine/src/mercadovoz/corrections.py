from __future__ import annotations

import copy
import re
from decimal import Decimal
from typing import Any

from .models import json_number, missing_fields, validate_operation
from .numbers import replace_number_words, strip_accents, to_decimal
from .parser import UNIT_ALIASES, confirmation_prompt

NUMBER = r"\d+(?:[.,]\d+)?"


def _normalize(text: str) -> str:
    text = strip_accents(text.lower())
    text = replace_number_words(text)
    return re.sub(r"\s+", " ", text).strip(" .,;")


def apply_correction(result: dict[str, Any], correction_text: str) -> dict[str, Any]:
    operation = copy.deepcopy(result.get("operation"))
    if not operation:
        return {
            "status": "UNRECOGNIZED",
            "operation": None,
            "missing_fields": [],
            "question": "No existe una operación pendiente que corregir.",
            "warnings": ["no_pending_operation"],
        }

    text = _normalize(correction_text)
    changed: list[str] = []

    explicit_patterns = {
        "quantity": rf"\b(?:cantidad|eran|fueron)\s+(?P<value>{NUMBER})\b",
        "unit_price": rf"\b(?:precio|era a|fue a)\s+\$?\s*(?P<value>{NUMBER})\b",
        "amount": rf"\b(?:importe|monto|fueron|era)\s+\$?\s*(?P<value>{NUMBER})(?:\s+dolares?)?\b",
    }
    for field, pattern in explicit_patterns.items():
        if field == "amount" and "amount" not in operation:
            continue
        if field == "quantity" and "quantity" not in operation:
            continue
        if field == "unit_price" and "unit_price" not in operation:
            continue
        match = re.search(pattern, text)
        if match:
            value = to_decimal(match.group("value"))
            operation[field] = json_number(value) if value is not None else None
            changed.append(field)
            break

    unit_match = re.search(r"\bunidad\s+(libra|libras|kilo|kilos|quintal|quintales|saco|sacos|caja|cajas|jaba|jabas|docena|docenas|funda|fundas)\b", text)
    if unit_match:
        operation["unit"] = UNIT_ALIASES[unit_match.group(1)]
        changed.append("unit")

    customer_match = re.search(r"\b(?:cliente|persona)\s+([a-zñ]+)\b", text)
    if customer_match and "customer" in operation:
        operation["customer"] = customer_match.group(1).title()
        changed.append("customer")

    product_match = re.search(r"\bproducto\s+([a-zñ][a-zñ\s]*)$", text)
    if product_match and "product" in operation:
        operation["product"] = product_match.group(1).strip()
        changed.append("product")

    if not changed:
        return {
            "status": "NEEDS_CONFIRMATION",
            "operation": operation,
            "missing_fields": missing_fields(operation),
            "question": "No entendí la corrección. Indique cantidad, precio, importe, unidad, producto o persona.",
            "warnings": ["correction_not_understood"],
        }

    if operation.get("quantity") is not None and operation.get("unit_price") is not None:
        total = Decimal(str(operation["quantity"])) * Decimal(str(operation["unit_price"]))
        operation["total"] = json_number(total)
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
