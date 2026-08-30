"""General, auditable rules layered in front of the frozen legacy parser."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from mercadovoz.models import json_number
from mercadovoz.parser import confirmation_prompt, normalize_text

UNIT_ALIASES = {
    "libra": "libra", "libras": "libra", "unidad": "unidad", "unidades": "unidad",
    "par": "par", "pares": "par", "vaso": "vaso", "vasos": "vaso",
    "caja": "caja", "cajas": "caja", "funda": "funda", "fundas": "funda",
    "jaba": "jaba", "jabas": "jaba", "saco": "saco", "sacos": "saco",
    "kilo": "kilo", "kilos": "kilo", "kg": "kilo",
    "docena": "docena", "docenas": "docena",
}
UNITS = "|".join(sorted(UNIT_ALIASES, key=len, reverse=True))
NUMBER = r"\d+(?:[.,]\d+)?"
MONEY = rf"(?:\$\s*)?{NUMBER}(?:\s+dolares?(?:\s+con\s+{NUMBER})?|\s+(?:centavos?|ctvs?))?"
SALE_VERBS = r"(?:vendi|vendimos|se\s+fueron|salieron|di)"
PRONOUNS = {"me", "te", "le", "lo", "la", "nos", "les", "se", "el", "ella", "ellos", "ellas"}


def _number(value: str) -> Decimal | None:
    try:
        return Decimal(value.replace(",", "."))
    except InvalidOperation:
        return None


def _money(value: str) -> Decimal | None:
    normalized = normalize_text(value).replace("$", " ")
    values = re.findall(NUMBER, normalized)
    if not values:
        return None
    amount = _number(values[0])
    if amount is None:
        return None
    if re.search(r"\b(?:centavos?|ctvs?)\b", normalized):
        return amount / Decimal("100")
    if len(values) > 1 and " con " in f" {normalized} ":
        cents = _number(values[1])
        if cents is None or cents >= 100:
            return None
        return amount + cents / Decimal("100")
    return amount


def _product(value: str) -> str | None:
    cleaned = re.sub(r"^[,;:\s]+|[,;:\s]+$", "", value)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or None


def _sale_body(value: str) -> tuple[Decimal, str, str] | None:
    body = re.sub(rf"^(?:hoy\s+)?{SALE_VERBS}\s+", "", value).strip(" ,")
    body = re.sub(rf"\s+{SALE_VERBS}$", "", body).strip(" ,")
    match = re.fullmatch(
        rf"(?P<quantity>{NUMBER})\s+(?P<unit>{UNITS})(?:\s+de)?\s+(?P<product>.+)", body,
    )
    if match:
        quantity, product = _number(match.group("quantity")), _product(match.group("product"))
        if quantity is not None and quantity > 0 and product:
            return quantity, UNIT_ALIASES[match.group("unit")], product
    match = re.fullmatch(rf"(?P<quantity>{NUMBER})\s+(?P<product>.+)", body)
    if match:
        quantity, product = _number(match.group("quantity")), _product(match.group("product"))
        starts_with_unit = bool(
            product and re.match(rf"^(?:{UNITS}|unidads|pars)\b", product)
        )
        if quantity is not None and quantity > 0 and product and not starts_with_unit:
            return quantity, "unidad", product
    match = re.fullmatch(
        rf"(?P<product>.+?)[,\s]+(?P<quantity>{NUMBER})\s+(?P<unit>{UNITS})", body,
    )
    if match:
        quantity, product = _number(match.group("quantity")), _product(match.group("product"))
        if quantity is not None and quantity > 0 and product:
            return quantity, UNIT_ALIASES[match.group("unit")], product
    return None


def _sale_result(
    body: str, *, unit_price: Decimal | None = None, stated_total: Decimal | None = None,
    warning: str | None = None,
) -> dict[str, Any] | None:
    parsed = _sale_body(body)
    if parsed is None:
        return None
    quantity, unit, product = parsed
    operation: dict[str, Any] = {
        "type": "SALE", "product": product, "quantity": json_number(quantity), "unit": unit,
    }
    computed: dict[str, Any] = {}
    if unit_price is not None:
        total = quantity * unit_price
        operation.update(unit_price=json_number(unit_price), total=json_number(total))
        computed["total"] = json_number(total)
    elif stated_total is not None:
        operation["total"] = json_number(stated_total)
    warnings = ["explicit_rules_v2"]
    if warning:
        warnings.append(warning)
    question = (
        confirmation_prompt(operation)
        if unit_price is not None
        else "Indique el precio por unidad antes de confirmar; conservaré el total declarado."
    )
    return {
        "status": "COMPLETE" if unit_price is not None else "NEEDS_CONFIRMATION",
        "operation": operation, "computed_fields": computed,
        "missing_fields": [], "question": question, "warnings": warnings,
    }


def _explicit_sale(text: str) -> dict[str, Any] | None:
    has_sale_verb = re.search(rf"\b{SALE_VERBS}\b", text) is not None
    has_explicit_unit_body = re.match(rf"^{NUMBER}\s+(?:{UNITS})\b", text) is not None
    if not has_sale_verb and not has_explicit_unit_body:
        return None
    total_match = re.fullmatch(
        rf"(?P<body>.+?)\s+(?:por\s+)?(?P<money>{MONEY})\s+(?:en\s+total|de\s+total|total|por\s+todo)", text,
    )
    if total_match:
        total = _money(total_match.group("money"))
        if total is not None:
            return _sale_result(total_match.group("body"), stated_total=total)
    patterns = (
        rf"(?P<body>.+?)\s+(?:a|por)\s+(?P<money>{MONEY})\s+"
        rf"(?:cada(?:\s+(?:1|una?|libras?|kilos?|kg|unidades?))?|por\s+unidad|la\s+(?:{UNITS}))",
        rf"(?P<body>.+?)\s+cada\s+(?:1|una?|libras?|kilos?|kg|unidades?)\s+(?:a|por)\s+(?P<money>{MONEY})",
        rf"(?P<body>.+?)\s+(?:a|por)\s+(?P<money>{MONEY})\s+(?:de\s+precio\s+unitario|precio\s+unitario)",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, text)
        if match:
            price = _money(match.group("money"))
            if price is not None:
                return _sale_result(match.group("body"), unit_price=price)
    match = re.fullmatch(r"(?P<body>.+?)\s+a\s+dolar(?:\s+cada\s+una?)?", text)
    if match:
        return _sale_result(match.group("body"), unit_price=Decimal("1"))
    # Bare "por <monto>" is a conventional bundle total and remains handled
    # by the frozen parser. Bare "a/en <monto>" does not identify the basis.
    match = re.fullmatch(rf"(?P<body>.+?)\s+(?:a|en)\s+(?P<money>{MONEY})", text)
    if match and _money(match.group("money")) is not None:
        return _sale_result(match.group("body"), warning="price_basis_ambiguous")
    return None


def _payment(text: str) -> dict[str, Any] | None:
    match = re.fullmatch(
        rf"(?:(?P<customer>[a-z][a-z\s]*?)\s+)?(?:(?:me|nos|le)\s+)?"
        rf"(?:abono|pago|dejo)\s+(?P<amount>{MONEY})", text,
    )
    if not match:
        return None
    amount = _money(match.group("amount"))
    if amount is None:
        return None
    operation: dict[str, Any] = {"type": "PAYMENT_RECEIVED", "amount": json_number(amount)}
    customer = _product(match.group("customer") or "")
    is_placeholder = bool(customer and re.match(r"^(?:nombre|cliente)(?:\s|$)", customer))
    if customer and customer not in PRONOUNS and not is_placeholder:
        operation["customer"] = customer.title()
    return {"status": "NEEDS_CONTEXT", "operation": operation, "warnings": ["explicit_rules_v2"]}


def parse_explicit_core(text: str) -> dict[str, Any] | None:
    normalized = normalize_text(text)
    logistics = re.fullmatch(
        rf"pague\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?\s+por\s+traer\s+(?:la\s+)?mercaderia", normalized,
    )
    if logistics:
        operation = {"type": "EXPENSE", "amount": json_number(Decimal(logistics.group("amount"))), "category": "logistica"}
        return {"status": "COMPLETE", "operation": operation, "question": confirmation_prompt(operation), "warnings": ["explicit_rules_v2"]}
    payment = _payment(normalized)
    return payment if payment is not None else _explicit_sale(normalized)
