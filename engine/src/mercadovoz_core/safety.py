from __future__ import annotations

import re
from dataclasses import dataclass

from mercadovoz.numbers import strip_accents


@dataclass(frozen=True)
class SafetyDecision:
    status: str
    warning: str
    question: str


def _plain(text: str) -> str:
    value = strip_accents(text.lower())
    value = re.sub(r"[^a-zñ0-9$.,\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def inspect_safety(text: str) -> SafetyDecision | None:
    """Block known high-severity interpretations before v0 normalizes text."""

    plain = _plain(text)

    if re.search(r"\b(?:como|aproximadamente|aprox|casi|unos|unas)\s+(?:\d+|[a-zñ]+)", plain) or "mas o menos" in plain:
        return SafetyDecision(
            "AMBIGUOUS",
            "approximate_amount_not_exact",
            "El valor parece aproximado. Indique el valor exacto antes de proponer el registro.",
        )

    if re.search(r"\b(?:saque|retiro|retire)\b", plain) and re.search(
        r"\b(?:para\b.{0,30}\bcasa|personal|mi plata|para mi|del negocio)\b", plain
    ):
        return SafetyDecision(
            "OUT_OF_SCOPE",
            "owner_withdrawal_schema_gap",
            "Parece un retiro personal; esa operación todavía no tiene un esquema aprobado.",
        )

    if re.search(r"\b(?:todavia|aun|sigue)\b.*\b(?:debe|debiendo)\b", plain) or re.search(
        r"\bdebe\b.*\b(?:ayer|antes|pendiente|lo de)\b", plain
    ):
        return SafetyDecision(
            "NEEDS_CONTEXT",
            "existing_receivable_state_not_event",
            "La frase describe una deuda existente. Seleccione la cuenta por cobrar; no crearé una deuda nueva.",
        )

    if re.search(r"\b(?:gaste|gastamos|pague)\b.*\b(?:almuerzo|comida|desayuno|cena)\b", plain):
        return SafetyDecision(
            "AMBIGUOUS",
            "personal_or_business_expense_ambiguous",
            "¿Fue un gasto del negocio o un gasto personal?",
        )

    signals = {
        "sale_or_income": r"\b(?:vendi|vendimos|venta|llevo|me entraron|me dieron|cobre)\b",
        "expense": r"\b(?:gaste|gastamos|gasto|pague|pago)\b",
        "receivable": r"\b(?:fiado|debe|debiendo|quedo fiada|quedo fiado)\b",
        "payment": r"\b(?:abono|me pago|me dejo|dejo)\b",
        "purchase": r"\b(?:compre|compramos|compra)\b",
        "stock": r"\b(?:stock|inventario|me quedan|quedaron|saque)\b",
    }
    matched = [name for name, pattern in signals.items() if re.search(pattern, plain)]
    if re.search(r"\by\b", plain) and len(matched) >= 2:
        return SafetyDecision(
            "COMPOUND_OPERATION",
            "compound_operation_requires_split",
            "Detecté más de una operación. Dígalas por separado para evitar mezclar importes o cantidades.",
        )

    # A quantity followed by a price can mean unit price or total unless the speaker says so.
    trade = re.search(
        r"\b(?:vendi|vendimos|compre|compramos)\s+(?:\d+|[a-zñ]+)\s+"
        r"(?:libra|libras|kilo|kilos|saco|sacos|caja|cajas|jaba|jabas|unidad|unidades|docena|docenas|funda|fundas)"
        r"\b.*\b(?:a|en)\s+\$?\s*(?:\d+|[a-zñ]+)(?:\s+dolares?)?\s*$",
        plain,
    )
    if trade and not re.search(r"\b(?:cada|en total|total)\b", plain):
        return SafetyDecision(
            "AMBIGUOUS",
            "price_basis_ambiguous",
            "¿Ese valor es el precio por unidad o el total de la operación?",
        )

    return None
