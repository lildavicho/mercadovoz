from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

from mercadovoz.models import json_number
from mercadovoz.parser import confirmation_prompt, normalize_text


UNIT_ALIASES = {
    "libra": "libra",
    "libras": "libra",
    "unidad": "unidad",
    "unidades": "unidad",
    "par": "par",
    "pares": "par",
    "vaso": "vaso",
    "vasos": "vaso",
    "caja": "caja",
    "cajas": "caja",
    "funda": "funda",
    "fundas": "funda",
    "jaba": "jaba",
    "jabas": "jaba",
    "saco": "saco",
    "sacos": "saco",
    "kilo": "kilo",
    "kilos": "kilo",
    "docena": "docena",
    "docenas": "docena",
}
UNITS = "|".join(sorted(UNIT_ALIASES, key=len, reverse=True))
NUMBER = r"\d+(?:[.,]\d+)?"


def _number(value: str) -> Decimal:
    return Decimal(value.replace(",", "."))


def parse_explicit_core(text: str) -> dict[str, Any] | None:
    """Parse narrow, explicit core patterns not covered by the frozen v0 parser."""

    normalized = normalize_text(text)

    logistics = re.fullmatch(
        rf"pague\s+\$?\s*(?P<amount>{NUMBER})(?:\s+dolares?)?\s+por\s+traer\s+(?:la\s+)?mercaderia",
        normalized,
    )
    if logistics:
        operation = {
            "type": "EXPENSE",
            "amount": json_number(_number(logistics.group("amount"))),
            "category": "logistica",
        }
        return {
            "status": "COMPLETE",
            "operation": operation,
            "missing_fields": [],
            "question": confirmation_prompt(operation),
            "warnings": ["explicit_rules_v1"],
        }

    sale = re.fullmatch(
        rf"(?:(?P<verb>vendi|se\s+fueron|salieron|di)\s+)?"
        rf"(?P<quantity>{NUMBER})\s+(?P<unit>{UNITS})(?:\s+de)?\s+"
        rf"(?P<product>[a-zñ][a-zñ\s]*?)\s+(?P<connector>a|por)\s+\$?\s*"
        rf"(?P<price>{NUMBER})(?:\s+dolares?)?\s+"
        rf"(?P<basis>cada\s+(?:1|uno|una)|la\s+(?:{UNITS}))",
        normalized,
    )
    if sale:
        quantity = _number(sale.group("quantity"))
        unit_price = _number(sale.group("price"))
        operation = {
            "type": "SALE",
            "product": sale.group("product").strip(),
            "quantity": json_number(quantity),
            "unit": UNIT_ALIASES[sale.group("unit")],
            "unit_price": json_number(unit_price),
            "total": json_number(quantity * unit_price),
        }
        return {
            "status": "COMPLETE",
            "operation": operation,
            "missing_fields": [],
            "question": confirmation_prompt(operation),
            "warnings": ["explicit_rules_v1"],
        }

    ambiguous_price = re.fullmatch(
        rf"(?P<verb>se\s+fueron|salieron|di)\s+"
        rf"(?P<quantity>{NUMBER})\s+(?P<unit>{UNITS})(?:\s+de)?\s+"
        rf"(?P<product>[a-zñ][a-zñ\s]*?)\s+(?:a|por)\s+\$?\s*(?P<price>{NUMBER})"
        rf"(?:\s+dolares?)?",
        normalized,
    )
    if ambiguous_price:
        operation = {
            "type": "SALE",
            "product": ambiguous_price.group("product").strip(),
            "quantity": json_number(_number(ambiguous_price.group("quantity"))),
            "unit": UNIT_ALIASES[ambiguous_price.group("unit")],
        }
        return {
            "status": "NEEDS_CONFIRMATION",
            "operation": operation,
            "missing_fields": ["unit_price", "total"],
            "question": "¿El valor indicado es precio por unidad o total?",
            "warnings": ["explicit_rules_v1", "price_basis_ambiguous"],
        }
    return None
