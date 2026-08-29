from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

from .models import json_number, missing_fields, validate_operation
from .numbers import replace_number_words, strip_accents, to_decimal

UNIT_ALIASES = {
    "libra": "libra",
    "libras": "libra",
    "kilo": "kilo",
    "kilos": "kilo",
    "quintal": "quintal",
    "quintales": "quintal",
    "saco": "saco",
    "sacos": "saco",
    "caja": "caja",
    "cajas": "caja",
    "jaba": "jaba",
    "jabas": "jaba",
    "unidad": "unidad",
    "unidades": "unidad",
    "docena": "docena",
    "docenas": "docena",
    "funda": "funda",
    "fundas": "funda",
}
UNITS_PATTERN = "|".join(sorted(UNIT_ALIASES, key=len, reverse=True))
NUMBER = r"\d+(?:[.,]\d+)?"


def normalize_text(text: str) -> str:
    normalized = strip_accents(text.lower()).replace("’", "'")
    normalized = replace_number_words(normalized)
    normalized = re.sub(r"[^a-zñ0-9$.,\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip(" .,;")
    return normalized


def classify_intent(text: str) -> str | None:
    if re.search(r"\b(me debe|me quedo debiendo|quedo debiendo|fiado)\b", text):
        return "RECEIVABLE"
    if re.search(r"\b(abono|me pago|pago (?:1|una) parte|me dejo)\b", text):
        return "PAYMENT_RECEIVED"
    if re.search(r"\b(gaste|gastamos)\b", text) or re.search(r"\bpague\b.+\b(en|de)\b", text):
        return "EXPENSE"
    if re.search(r"\b(vendi|vendimos)\b", text):
        return "SALE"
    if re.search(r"\b(compre|compramos)\b", text):
        return "PURCHASE"
    if re.search(r"\b(me quedan|quedaron|entraron|saque)\b", text):
        return "STOCK_ADJUSTMENT"
    return None


def _clean_label(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"\b(dolar|dolares|cada 1|cada uno|cada una)\b", "", value)
    value = re.sub(r"\s+", " ", value).strip(" .,;")
    return value or None


def _parse_trade(text: str, operation_type: str) -> dict[str, Any]:
    verb = r"(?:vendi|vendimos)" if operation_type == "SALE" else r"(?:compre|compramos)"
    operation: dict[str, Any] = {"type": operation_type}
    detailed = re.search(
        rf"\b{verb}\s+(?P<quantity>{NUMBER})\s+(?P<unit>{UNITS_PATTERN})"
        rf"(?:\s+de)?\s+(?P<product>[a-zñ][a-zñ\s]*?)"
        rf"(?:\s+(?P<connector>a|por)\s+\$?\s*(?P<price>{NUMBER})"
        rf"(?:\s+dolares?)?(?:\s+cada\s+(?:1|uno|una))?)?$",
        text,
    )
    if detailed:
        quantity = to_decimal(detailed.group("quantity"))
        price = to_decimal(detailed.group("price"))
        operation.update(
            product=_clean_label(detailed.group("product")),
            quantity=json_number(quantity) if quantity is not None else None,
            unit=UNIT_ALIASES[detailed.group("unit")],
        )
        connector = detailed.group("connector")
        if quantity is not None and price is not None:
            if connector == "a":
                operation["unit_price"] = json_number(price)
                operation["total"] = json_number(quantity * price)
            elif connector == "por":
                operation["total"] = json_number(price)
                operation["unit_price"] = json_number(price / quantity)
        return operation

    partial = re.search(
        rf"\b{verb}\s+(?P<body>.+?)(?:\s+(?P<connector>a|por)\s+\$?\s*(?P<price>{NUMBER})(?:\s+dolares?)?)?$",
        text,
    )
    if not partial:
        return operation
    body = partial.group("body")
    quantity_match = re.match(rf"(?P<quantity>{NUMBER})\s+(?P<rest>.+)", body)
    if quantity_match:
        quantity = to_decimal(quantity_match.group("quantity"))
        operation["quantity"] = json_number(quantity) if quantity is not None else None
        body = quantity_match.group("rest")
    unit_match = re.match(rf"(?P<unit>{UNITS_PATTERN})(?:\s+de)?\s*(?P<product>.*)", body)
    if unit_match:
        operation["unit"] = UNIT_ALIASES[unit_match.group("unit")]
        operation["product"] = _clean_label(unit_match.group("product"))
    else:
        operation["product"] = _clean_label(body)
    price = to_decimal(partial.group("price"))
    if price is not None:
        if partial.group("connector") == "a":
            operation["unit_price"] = json_number(price)
        else:
            operation["total"] = json_number(price)
    return operation


def _parse_expense(text: str) -> dict[str, Any]:
    operation: dict[str, Any] = {"type": "EXPENSE"}
    match = re.search(
        rf"\b(?:gaste|gastamos|pague)\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?\s+(?:en|de)\s+(?P<category>[a-zñ][a-zñ\s]*)$",
        text,
    )
    reverse = re.search(
        rf"\b(?:gaste|gastamos)\s+(?:en|de)\s+(?P<category>[a-zñ][a-zñ\s]*?)\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?$",
        text,
    )
    match = match or reverse
    if match:
        amount = to_decimal(match.group("amount"))
        operation["amount"] = json_number(amount) if amount is not None else None
        operation["category"] = _clean_label(match.group("category"))
    return operation


def _parse_receivable(text: str) -> dict[str, Any]:
    operation: dict[str, Any] = {"type": "RECEIVABLE"}
    patterns = [
        rf"^(?P<customer>[a-zñ]+)\s+(?:me debe|me quedo debiendo)\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?$",
        rf"^(?:me debe|me quedo debiendo)\s+(?P<customer>[a-zñ]+)\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount = to_decimal(match.group("amount"))
            operation["customer"] = match.group("customer").title()
            operation["amount"] = json_number(amount) if amount is not None else None
            break
    if "amount" not in operation:
        amount_match = re.search(rf"\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?", text)
        if amount_match:
            amount = to_decimal(amount_match.group("amount"))
            operation["amount"] = json_number(amount) if amount is not None else None
    return operation


def _parse_payment(text: str) -> dict[str, Any]:
    operation: dict[str, Any] = {"type": "PAYMENT_RECEIVED"}
    patterns = [
        rf"^(?P<customer>[a-zñ]+)\s+(?:abono|me pago|pago (?:1|una) parte(?: de)?|me dejo)\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?$",
        rf"^(?:abono|me pago)\s+(?P<customer>[a-zñ]+)\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount = to_decimal(match.group("amount"))
            operation["customer"] = match.group("customer").title()
            operation["amount"] = json_number(amount) if amount is not None else None
            break
    if "amount" not in operation:
        amount_match = re.search(rf"(?:\$\s*|(?<!\w))(?P<amount>{NUMBER})\s+dolares?\b", text)
        if not amount_match and re.match(r"^abono\b", text):
            amount_match = re.search(rf"\b(?P<amount>{NUMBER})\b", text)
        if amount_match:
            amount = to_decimal(amount_match.group("amount"))
            operation["amount"] = json_number(amount) if amount is not None else None
    return operation


def _parse_stock(text: str) -> dict[str, Any]:
    operation: dict[str, Any] = {"type": "STOCK_ADJUSTMENT"}
    modes = {
        "me quedan": "SET",
        "quedaron": "SET",
        "entraron": "INCREASE",
        "saque": "DECREASE",
    }
    match = re.search(
        rf"\b(?P<verb>me quedan|quedaron|entraron|saque)\s+(?P<quantity>{NUMBER})\s+"
        rf"(?P<unit>{UNITS_PATTERN})(?:\s+de)?\s+(?P<product>[a-zñ][a-zñ\s]*)$",
        text,
    )
    if match:
        quantity = to_decimal(match.group("quantity"))
        operation.update(
            quantity=json_number(quantity) if quantity is not None else None,
            unit=UNIT_ALIASES[match.group("unit")],
            product=_clean_label(match.group("product")),
            mode=modes[match.group("verb")],
        )
    return operation


def _question_for(operation: dict[str, Any], missing: list[str]) -> str:
    labels = {
        "product": "el producto",
        "quantity": "la cantidad",
        "unit": "la unidad",
        "unit_price": "el precio por unidad",
        "total": "el total",
        "category": "la categoría del gasto",
        "amount": "el importe",
        "customer": "la persona",
        "mode": "si el stock aumenta, disminuye o queda fijado",
    }
    if missing:
        readable = ", ".join(labels.get(field, field) for field in missing)
        return f"Necesito confirmar {readable}."
    return "Necesito confirmar esta operación antes de registrarla."


def confirmation_prompt(operation: dict[str, Any]) -> str:
    operation_type = operation["type"]
    if operation_type in {"SALE", "PURCHASE"}:
        action = "venta" if operation_type == "SALE" else "compra"
        return (
            f"Interpreté una {action} de {operation['quantity']} {operation['unit']}(s) de "
            f"{operation['product']} a ${operation['unit_price']} cada una, total ${operation['total']}. ¿Correcto?"
        )
    if operation_type == "EXPENSE":
        return f"Interpreté un gasto de ${operation['amount']} en {operation['category']}. ¿Correcto?"
    if operation_type == "RECEIVABLE":
        return f"Interpreté que {operation['customer']} debe ${operation['amount']}. ¿Correcto?"
    if operation_type == "PAYMENT_RECEIVED":
        return f"Interpreté un abono de {operation['customer']} por ${operation['amount']}. ¿Correcto?"
    return (
        f"Interpreté un ajuste {operation['mode']} de {operation['quantity']} "
        f"{operation['unit']}(s) de {operation['product']}. ¿Correcto?"
    )


def parse_text(text: str) -> dict[str, Any]:
    started_text = text.strip()
    normalized = normalize_text(started_text)
    intent_signals = (
        r"\b(vendi|vendimos|venta)\b",
        r"\b(compre|compramos|compra)\b",
        r"\b(gaste|gastamos|gasto|pague)\b",
        r"\b(debe|debiendo|fiado)\b",
        r"\b(abono|abono|pago|pago)\b",
        r"\b(stock|inventario|quedan|quedo)\b",
    )
    compound = bool(
        re.search(r"\by\b", normalized)
        and sum(bool(re.search(pattern, normalized)) for pattern in intent_signals) > 1
    )
    primary_text = normalized.split(" y ", 1)[0] if compound else normalized
    operation_type = classify_intent(primary_text) or classify_intent(normalized)
    if not operation_type:
        return {
            "status": "UNRECOGNIZED",
            "operation": None,
            "missing_fields": [],
            "question": "No pude reconocer una operación comercial soportada.",
            "warnings": [],
        }
    if compound:
        return {
            "status": "NEEDS_CONFIRMATION",
            "operation": {"type": operation_type},
            "missing_fields": [],
            "question": "Detecté más de una operación; en Sprint 0 deben registrarse por separado.",
            "warnings": ["compound_operation_out_of_scope"],
        }
    if operation_type in {"SALE", "PURCHASE"}:
        operation = _parse_trade(normalized, operation_type)
    elif operation_type == "EXPENSE":
        operation = _parse_expense(normalized)
    elif operation_type == "RECEIVABLE":
        operation = _parse_receivable(normalized)
    elif operation_type == "PAYMENT_RECEIVED":
        operation = _parse_payment(normalized)
    else:
        operation = _parse_stock(normalized)

    missing = missing_fields(operation)
    validation_errors = validate_operation(operation)
    warnings: list[str] = []
    if operation_type in {"PURCHASE", "STOCK_ADJUSTMENT"}:
        warnings.append("exploratory_operation_not_in_go_metric")
    if compound:
        warnings.append("compound_operation_out_of_scope")

    needs_confirmation = bool(missing or validation_errors or compound)
    if needs_confirmation:
        return {
            "status": "NEEDS_CONFIRMATION",
            "operation": operation,
            "missing_fields": missing,
            "question": (
                "Detecté más de una operación; en Sprint 0 deben registrarse por separado."
                if compound
                else _question_for(operation, missing)
            ),
            "warnings": warnings + validation_errors,
        }
    return {
        "status": "COMPLETE",
        "operation": operation,
        "missing_fields": [],
        "question": confirmation_prompt(operation),
        "warnings": warnings,
    }
