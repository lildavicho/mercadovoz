from __future__ import annotations

import re
import time
from copy import deepcopy
from decimal import Decimal
from typing import Any
from uuid import uuid4

from mercadovoz.models import json_number
from mercadovoz.numbers import HUNDREDS, SMALL, TENS, strip_accents, to_decimal
from mercadovoz.parser import normalize_text
from mercadovoz_core.context import ContextSession
from mercadovoz_core.engine import MercadoVozEngine

from .segmenter import CommercialNarrativeSegmenter, NarrativeSegment
from .versioning import (
    BATCH_SCHEMA_VERSION,
    ENGINE_VERSION,
    SEGMENTER_VERSION,
    UNDERLYING_ENGINE_VERSION,
)


CONFIRMABLE_STATES = {"COMPLETE"}
BLOCKING_STATES = {
    "NEEDS_CONFIRMATION",
    "NEEDS_CONTEXT",
    "AMBIGUOUS",
    "COMPOUND_OPERATION",
    "OUT_OF_SCOPE",
    "UNSAFE",
    "UNRECOGNIZED",
}

_EXPLICIT_DEBT = re.compile(
    r"(?i)^\s*(?P<customer>[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúÑñ-]*(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúÑñ-]*)?)"
    r"\s+(?:qued(?:ó|o)\s+debiendo|me\s+debe)\s+\$?\s*(?P<amount>\d+(?:[.,]\d+)?)"
    r"(?:\s+dólares?)?\s*$"
)
_SETTLEMENT = re.compile(
    r"(?i)^\s*(?P<customer>[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúÑñ-]*(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúÑñ-]*)?)"
    r"\s+(?:llev(?:ó|o)|compr(?:ó|o))\s+\$?\s*(?P<total>\d+(?:[.,]\d+)?)"
    r"(?:\s+dólares?)?(?:\s+de\s+producto)?\s+y\s+(?:me\s+)?(?:dej(?:ó|o)|pag(?:ó|o))"
    r"\s+\$?\s*(?P<paid>\d+(?:[.,]\d+)?)(?:\s+dólares?)?\s*$"
)
_LINE_ITEM = re.compile(
    r"(?i)(?P<quantity>\d+(?:[.,]\d+)?)\s+(?P<product>[a-záéíóúñ][a-záéíóúñ\s-]*?)"
    r"\s+(?:a|por)\s+\$?\s*(?P<price>\d+(?:[.,]\d+)?)"
    r"\s*(?P<cents>centavos?|ctvs?)?(?:\s+dolar(?:es)?)?\s+cada(?:\s+(?:uno|una|1))?"
    r"(?=\s+(?:y|,)|$)"
)

_SIMPLE_NUMBERS = {**SMALL, **TENS, **HUNDREDS}


def _number(value: str) -> Decimal | None:
    return to_decimal(value.replace(",", "."))


def _replace_simple_number_words(value: str) -> str:
    plain = strip_accents(value.lower())
    pattern = re.compile(r"\b(?:" + "|".join(sorted(_SIMPLE_NUMBERS, key=len, reverse=True)) + r")\b")
    return pattern.sub(lambda match: str(_SIMPLE_NUMBERS[match.group(0)]), plain)


def _source(start: int, end: int, *, derived: bool = False, formula: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "source": "DERIVED" if derived else "EXPLICIT",
        "derived": derived,
        "source_span": {"start": start, "end": end},
    }
    if formula:
        result["formula"] = formula
    return result


class BatchInterpreter:
    """Engine 1.2 sidecar that composes, but never mutates, Engine 1.1."""

    def __init__(
        self,
        *,
        single_engine: MercadoVozEngine | None = None,
        segmenter: CommercialNarrativeSegmenter | None = None,
    ) -> None:
        self.single_engine = single_engine or MercadoVozEngine()
        self.segmenter = segmenter or CommercialNarrativeSegmenter()

    def interpret(
        self,
        text: str,
        context: ContextSession | None = None,
        *,
        input_mode: str = "TEXT_BATCH",
    ) -> dict[str, Any]:
        started = time.perf_counter()
        batch_id = str(uuid4())
        if input_mode not in {"TEXT_SINGLE", "TEXT_BATCH", "VOICE_TRANSCRIPT"}:
            raise ValueError("unsupported input mode")
        try:
            narrative_segments = self.segmenter.segment(text)
        except ValueError as exc:
            return self._blocked(batch_id, text, input_mode, str(exc), started)
        if not narrative_segments:
            return self._blocked(batch_id, text, input_mode, "empty_input", started)

        items: list[dict[str, Any]] = []
        groups: list[dict[str, Any]] = []
        for source_segment in narrative_segments:
            settlement = self._settlement_items(source_segment)
            if settlement:
                group, group_items = settlement
                groups.append(group)
                items.extend(group_items)
                continue
            items.append(self._interpret_segment(source_segment, context))

        status = self._batch_status(items)
        return {
            "batch_id": batch_id,
            "source_text": text,
            "input_mode": input_mode,
            "engine_version": ENGINE_VERSION,
            "underlying_engine_version": UNDERLYING_ENGINE_VERSION,
            "schema_version": BATCH_SCHEMA_VERSION,
            "segmenter_version": SEGMENTER_VERSION,
            "segments": items,
            "groups": groups,
            "warnings": list(dict.fromkeys(
                warning for item in items for warning in item.get("warnings", [])
            )),
            "status": status,
            "confirmable_item_ids": [item["segment_id"] for item in items if item["confirmable"]],
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        }

    def _blocked(
        self, batch_id: str, text: str, input_mode: str, warning: str, started: float
    ) -> dict[str, Any]:
        return {
            "batch_id": batch_id,
            "source_text": text,
            "input_mode": input_mode,
            "engine_version": ENGINE_VERSION,
            "underlying_engine_version": UNDERLYING_ENGINE_VERSION,
            "schema_version": BATCH_SCHEMA_VERSION,
            "segmenter_version": SEGMENTER_VERSION,
            "segments": [],
            "groups": [],
            "warnings": [warning],
            "status": "BLOCKED",
            "confirmable_item_ids": [],
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        }

    def _interpret_segment(
        self, source: NarrativeSegment, context: ContextSession | None
    ) -> dict[str, Any]:
        line_items = self._line_item_sale(source)
        if line_items:
            return line_items
        result = self.single_engine.interpret(source.text, context)
        result = self._adapt_explicit_debt(source, result)
        result = self._adapt_explicit_total_sale(source, result)
        operation = deepcopy(result.get("operation"))
        computed = deepcopy(result.get("computed_fields", {}))
        provenance: dict[str, Any] = {}
        if operation:
            for field in operation:
                if field == "type":
                    continue
                provenance[field] = _source(
                    source.start,
                    source.end,
                    derived=field in computed,
                    formula=f"Engine 1.1 computed {field}" if field in computed else None,
                )
        return self._item(
            source=source,
            operation=operation,
            state=result["status"],
            warnings=result.get("warnings", []),
            context_used=result.get("context_used", []),
            computed_fields=computed,
            field_provenance=provenance,
        )

    def _adapt_explicit_debt(
        self, source: NarrativeSegment, result: dict[str, Any]
    ) -> dict[str, Any]:
        normalized = normalize_text(source.text)
        match = re.fullmatch(
            r"(?P<customer>[a-zñ][a-zñ\s-]*?)\s+(?:quedo\s+debiendo|me\s+debe)\s+"
            r"(?P<amount>\d+(?:[.,]\d+)?)(?:\s+dolares?)?",
            normalized,
        )
        if not match:
            return result
        amount = _number(match.group("amount"))
        if amount is None or amount <= 0:
            return result
        customer_original = source.text[: source.text.lower().find(" quedó")]
        if customer_original == source.text:
            customer_original = match.group("customer").title()
        return {
            **result,
            "status": "COMPLETE",
            "operation": {
                "type": "RECEIVABLE",
                "customer": customer_original.strip().title(),
                "amount": json_number(amount),
            },
            "fields_extracted": {
                "type": "RECEIVABLE",
                "customer": customer_original.strip().title(),
                "amount": json_number(amount),
            },
            "missing_fields": [],
            "warnings": [*result.get("warnings", []), "batch_explicit_new_debt"],
        }

    def _adapt_explicit_total_sale(
        self, source: NarrativeSegment, result: dict[str, Any]
    ) -> dict[str, Any]:
        operation = deepcopy(result.get("operation"))
        if not operation or operation.get("type") != "SALE":
            return result
        if operation.get("total") is None or "en total" not in normalize_text(source.text):
            return result
        operation["unit_price"] = None
        return {
            **result,
            "status": "COMPLETE",
            "operation": operation,
            "fields_extracted": deepcopy(operation),
            "missing_fields": [],
            "warnings": [
                warning for warning in result.get("warnings", []) if warning != "missing:unit_price"
            ] + ["explicit_total_without_unit_price"],
        }

    def _line_item_sale(self, source: NarrativeSegment) -> dict[str, Any] | None:
        # Do not use the frozen normalizer here: its general number-word pass
        # intentionally folds numeric coordination ("uno y tres") and would
        # destroy a line-item boundary. This lexical pass replaces each simple
        # number independently and leaves conjunctions intact.
        normalized = _replace_simple_number_words(source.text)
        if not normalized.startswith(("vendi ", "vendimos ")):
            return None
        body = re.sub(r"^(?:vendi|vendimos)\s+", "", normalized)
        matches = list(_LINE_ITEM.finditer(body))
        if len(matches) < 2:
            return None
        line_items: list[dict[str, Any]] = []
        total = Decimal("0")
        for match in matches:
            quantity = _number(match.group("quantity"))
            price = _number(match.group("price"))
            if quantity is None or price is None or quantity <= 0 or price <= 0:
                return None
            if match.group("cents"):
                price /= Decimal("100")
            line_total = quantity * price
            line_items.append({
                "line_item_id": str(uuid4()),
                "product": match.group("product").strip(),
                "quantity": json_number(quantity),
                "unit": "unidad",
                "unit_price": json_number(price),
                "total": json_number(line_total),
            })
            total += line_total
        operation = {"type": "SALE", "line_items": line_items, "total": json_number(total)}
        provenance = {
            "line_items": _source(source.start, source.end),
            "total": _source(
                source.start,
                source.end,
                derived=True,
                formula="sum(line_items.quantity * line_items.unit_price)",
            ),
        }
        return self._item(
            source=source,
            operation=operation,
            state="COMPLETE",
            warnings=["batch_line_items_v1"],
            computed_fields={"total": operation["total"]},
            field_provenance=provenance,
        )

    def _settlement_items(
        self, source: NarrativeSegment
    ) -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
        normalized = normalize_text(source.text)
        match = re.fullmatch(
            r"(?P<customer>[a-zñ][a-zñ\s-]*?)\s+(?:llevo|compro)\s+"
            r"(?P<total>\d+(?:[.,]\d+)?)(?:\s+dolares?)?(?:\s+de\s+producto)?\s+"
            r"y\s+(?:me\s+)?(?:dejo|pago)\s+(?P<paid>\d+(?:[.,]\d+)?)(?:\s+dolares?)?",
            normalized,
        )
        if not match:
            return None
        total = _number(match.group("total"))
        paid = _number(match.group("paid"))
        if total is None or paid is None or total <= 0 or paid < 0 or paid > total:
            return None
        customer = re.split(
            r"(?i)\s+(?:llevó|llevo|compró|compro)\b", source.text, maxsplit=1
        )[0].strip().title()
        group_id = str(uuid4())
        remaining = total - paid
        base = {
            "sequence": source.sequence,
            "start": source.start,
            "end": source.end,
            "text": source.text,
        }
        definitions = [
            ({"type": "SALE", "customer": customer, "total": json_number(total), "unit_price": None}, {}),
            ({"type": "PAYMENT_RECEIVED", "customer": customer, "amount": json_number(paid), "settlement_role": "PAYMENT_AT_SALE"}, {}),
        ]
        if remaining > 0:
            definitions.append((
                {"type": "RECEIVABLE", "customer": customer, "amount": json_number(remaining)},
                {"amount": _source(source.start, source.end, derived=True, formula="sale.total - payment.amount")},
            ))
        items: list[dict[str, Any]] = []
        for index, (operation, special_provenance) in enumerate(definitions, start=1):
            item_source = NarrativeSegment(
                sequence=source.sequence,
                start=source.start,
                end=source.end,
                text=source.text,
            )
            provenance = {
                field: _source(source.start, source.end)
                for field in operation if field != "type"
            }
            provenance.update(special_provenance)
            item = self._item(
                source=item_source,
                operation=operation,
                state="COMPLETE",
                warnings=["sale_settlement_requires_human_confirmation"],
                computed_fields={"amount": operation.get("amount")} if special_provenance else {},
                field_provenance=provenance,
            )
            item["segment_id"] = f"{item['segment_id']}-{index}"
            item["transaction_group_id"] = group_id
            if index > 1:
                item["depends_on"] = [items[0]["segment_id"]]
            items.append(item)
        group = {
            "group_id": group_id,
            "type": "SALE_SETTLEMENT",
            "customer": customer,
            "related_segment_ids": [item["segment_id"] for item in items],
            "derived_relationships": [
                {
                    "relationship": "OUTSTANDING_EQUALS_SALE_MINUS_PAYMENT",
                    "derived": True,
                    "formula": "sale.total - payment.amount",
                }
            ] if remaining > 0 else [],
        }
        return group, items

    @staticmethod
    def _item(
        *,
        source: NarrativeSegment,
        operation: dict[str, Any] | None,
        state: str,
        warnings: list[str],
        context_used: list[dict[str, Any]] | None = None,
        computed_fields: dict[str, Any] | None = None,
        field_provenance: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "segment_id": str(uuid4()),
            "sequence": source.sequence,
            "source_span": {"start": source.start, "end": source.end},
            "source_text": source.text,
            "state": state,
            "operation": operation,
            "fields_extracted": deepcopy(operation) if operation else {},
            "computed_fields": computed_fields or {},
            "field_provenance": field_provenance or {},
            "context_used": context_used or [],
            "warnings": list(warnings),
            "depends_on": [],
            "confirmable": state in CONFIRMABLE_STATES and operation is not None,
        }

    @staticmethod
    def _batch_status(items: list[dict[str, Any]]) -> str:
        confirmable = sum(1 for item in items if item["confirmable"])
        if confirmable == len(items) and items:
            return "READY"
        if confirmable:
            return "PARTIALLY_READY"
        if any(item["state"] in {"NEEDS_CONFIRMATION", "NEEDS_CONTEXT", "AMBIGUOUS"} for item in items):
            return "NEEDS_REVIEW"
        return "BLOCKED"
