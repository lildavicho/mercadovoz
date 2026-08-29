from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from mercadovoz import parse_text
from mercadovoz_core import MercadoVozEngine


CORE_TYPES = {"SALE", "EXPENSE", "RECEIVABLE", "PAYMENT_RECEIVED"}
EXPLICIT_CORE_PHENOMENA = {
    "EXPLICIT_QUANTITY_UNIT_PRICE",
    "BUSINESS_EXPENSE",
    "LOGISTICS_EXPENSE",
    "NEW_RECEIVABLE",
}
MONEY_SAFETY_PHENOMENA = {
    "OWNER_WITHDRAWAL_SCHEMA_GAP",
    "OWNER_CONTRIBUTION_SCHEMA_GAP",
    "APPROXIMATE_DAILY_CLOSE",
    "PRICE_TOTAL_AMBIGUITY",
    "STATE_VS_EVENT",
    "NUMERIC_COORDINATION_CINCO_Y_UNA",
    "COMPOUND_INCOME_EXPENSE",
    "COMPOUND_PAYMENT_PURCHASE",
    "COMPOUND_SALE_PARTIAL_PAYMENT",
    "COMPOUND_SALE_RECEIVABLE_NUMERIC_COORDINATION",
}
SAFE_STATUSES = {
    "NEEDS_CONFIRMATION",
    "NEEDS_CONTEXT",
    "AMBIGUOUS",
    "COMPOUND_OPERATION",
    "OUT_OF_SCOPE",
    "UNSAFE",
    "UNRECOGNIZED",
}


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _same(expected: Any, predicted: Any) -> bool:
    if isinstance(expected, (int, float)) and isinstance(predicted, (int, float)):
        return abs(float(expected) - float(predicted)) <= 0.01
    category_aliases = {"transport": "transporte", "logistics": "logistica"}
    if isinstance(expected, str) and isinstance(predicted, str):
        expected_text = category_aliases.get(expected, expected)
        fold = lambda value: "".join(
            char
            for char in __import__("unicodedata").normalize("NFD", value.casefold())
            if __import__("unicodedata").category(char) != "Mn"
        )
        return fold(expected_text) == fold(predicted)
    return expected == predicted


def _is_compound_detected(prediction: dict[str, Any]) -> bool:
    return prediction.get("status") == "COMPOUND_OPERATION" or any(
        "compound_operation" in warning for warning in prediction.get("warnings", [])
    )


def _has_exact_numeric_operation(prediction: dict[str, Any]) -> bool:
    operation = prediction.get("operation") or {}
    return any(operation.get(field) is not None for field in ("amount", "quantity", "unit_price", "total"))


def critical_violation(row: dict[str, Any], prediction: dict[str, Any]) -> str | None:
    phenomenon = row["phenomenon"]
    operation = prediction.get("operation") or {}
    operation_type = operation.get("type")
    status = prediction.get("status")

    if phenomenon == "OWNER_WITHDRAWAL_SCHEMA_GAP" and operation_type == "STOCK_ADJUSTMENT":
        return "owner_withdrawal_as_stock"
    if phenomenon == "OWNER_CONTRIBUTION_SCHEMA_GAP" and operation_type in CORE_TYPES:
        return "owner_contribution_as_core_operation"
    if phenomenon == "APPROXIMATE_DAILY_CLOSE" and _has_exact_numeric_operation(prediction):
        return "approximation_made_exact"
    if phenomenon == "STATE_VS_EVENT" and operation_type == "RECEIVABLE":
        return "state_created_receivable"
    if row["expected_operation"] == "COMPOUND_OPERATION" and status == "COMPLETE" and operation_type:
        return "compound_finalized_as_single_operation"
    if phenomenon in {
        "NUMERIC_COORDINATION_CINCO_Y_UNA",
        "COMPOUND_SALE_RECEIVABLE_NUMERIC_COORDINATION",
    } and operation.get("quantity") == 6:
        return "numeric_coordination_false_sum"
    if phenomenon == "PRICE_TOTAL_AMBIGUITY" and status == "COMPLETE":
        return "ambiguous_price_finalized"
    return None


def _load_ids(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def evaluate(
    path: Path,
    engine_name: str,
    *,
    include_ids: set[str] | None = None,
    exclude_ids: set[str] | None = None,
) -> dict[str, Any]:
    rows = load_rows(path)
    if include_ids is not None:
        rows = [row for row in rows if row["id"] in include_ids]
    if exclude_ids:
        rows = [row for row in rows if row["id"] not in exclude_ids]
    if engine_name == "v0":
        interpret: Callable[[str], dict[str, Any]] = parse_text
        version = "rules-v0.1.0"
    else:
        engine = MercadoVozEngine()
        interpret = engine.interpret
        version = engine.parser_version

    explicit = {"cases": 0, "intent_correct": 0, "fields_correct": 0, "fields_total": 0, "exact": 0}
    context = {"cases": 0, "context_requested": 0, "safe": 0, "unsafe_finalization": 0}
    compound = {"cases": 0, "detected": 0, "unsafe_single_operation": 0}
    money = {"cases": 0, "critical_violations": 0}
    out_scope = {"cases": 0, "safe": 0}
    violations: Counter[str] = Counter()
    per_phenomenon: dict[str, Counter[str]] = defaultdict(Counter)
    statuses: Counter[str] = Counter()
    latencies: list[float] = []
    case_results: list[dict[str, Any]] = []

    for row in rows:
        started = time.perf_counter()
        predicted = interpret(row["text"])
        latencies.append((time.perf_counter() - started) * 1000)
        status = predicted.get("status")
        statuses[status] += 1
        predicted_operation = predicted.get("operation") or {}
        expected_fields = row.get("expected") or {}
        phenomenon = row["phenomenon"]

        if phenomenon in EXPLICIT_CORE_PHENOMENA:
            explicit["cases"] += 1
            intent_ok = predicted_operation.get("type") == row["expected_operation"]
            explicit["intent_correct"] += intent_ok
            fields_ok = intent_ok
            for field, value in expected_fields.items():
                explicit["fields_total"] += 1
                match = _same(value, predicted_operation.get(field))
                explicit["fields_correct"] += match
                fields_ok = fields_ok and match
            explicit["exact"] += fields_ok

        if row["safety_expectation"] == "NEEDS_CONTEXT":
            context["cases"] += 1
            context["context_requested"] += status == "NEEDS_CONTEXT"
            is_safe = status in SAFE_STATUSES
            context["safe"] += is_safe
            context["unsafe_finalization"] += not is_safe

        if row["expected_operation"] == "COMPOUND_OPERATION":
            compound["cases"] += 1
            detected = _is_compound_detected(predicted)
            compound["detected"] += detected
            unsafe_single = status == "COMPLETE" and bool(predicted_operation.get("type"))
            compound["unsafe_single_operation"] += unsafe_single

        if phenomenon in MONEY_SAFETY_PHENOMENA:
            money["cases"] += 1
            violation = critical_violation(row, predicted)
            if violation:
                money["critical_violations"] += 1
                violations[violation] += 1

        if row["safety_expectation"] in {"OUT_OF_SCOPE_OR_CONFIRM", "OUT_OF_CORE_OR_CONFIRM"}:
            out_scope["cases"] += 1
            out_scope["safe"] += status in SAFE_STATUSES

        per_phenomenon[phenomenon]["cases"] += 1
        per_phenomenon[phenomenon][f"status:{status}"] += 1
        case_results.append(
            {
                "id": row["id"],
                "text": row["text"],
                "source_id": row["source_id"],
                "phenomenon": phenomenon,
                "safety_expectation": row["safety_expectation"],
                "expected_operation": row["expected_operation"],
                "expected": expected_fields,
                "critical_violation": critical_violation(row, predicted),
                "predicted": predicted,
            }
        )

    def rate(numerator: int, denominator: int) -> float | None:
        return numerator / denominator if denominator else None

    metrics = {
        "explicit_core": {
            **explicit,
            "intent_accuracy": rate(explicit["intent_correct"], explicit["cases"]),
            "available_field_accuracy": rate(explicit["fields_correct"], explicit["fields_total"]),
            "exact_annotated_operation_accuracy": rate(explicit["exact"], explicit["cases"]),
        },
        "context_required": {
            **context,
            "correct_context_request_rate": rate(context["context_requested"], context["cases"]),
            "safe_context_handling_rate": rate(context["safe"], context["cases"]),
            "unsafe_finalization_rate": rate(context["unsafe_finalization"], context["cases"]),
        },
        "compound": {
            **compound,
            "compound_detection_recall": rate(compound["detected"], compound["cases"]),
            "unsafe_single_operation_rate": rate(compound["unsafe_single_operation"], compound["cases"]),
        },
        "money_safety": {
            **money,
            "unsafe_financial_inference_rate": rate(money["critical_violations"], money["cases"]),
            "violation_types": dict(sorted(violations.items())),
        },
        "out_of_scope": {
            **out_scope,
            "safe_abstention_rate": rate(out_scope["safe"], out_scope["cases"]),
        },
    }
    return {
        "dataset": {
            "dataset_version": "external-cuenca-v1",
            "path": str(path),
            "sha256": "02558a7450035b712c95eb240016efc716a47c3fc66feb57ee62a68ea8bd2788",
            "records": len(rows),
            "provenance_type": "WEB_DERIVED_MULTISOURCE",
            "real_participant": False,
            "eligible_for_real_heldout": False,
        },
        "engine": {"name": engine_name, "version": version, "model": None, "estimated_cost_usd": 0.0},
        "metrics": metrics,
        "predicted_statuses": dict(sorted(statuses.items())),
        "latency_ms": {
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "max": max(latencies),
        },
        "per_phenomenon": {key: dict(value) for key, value in sorted(per_phenomenon.items())},
        "case_results": case_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--engine", choices=("v0", "v1"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-ids", type=Path)
    parser.add_argument("--exclude-ids", type=Path)
    args = parser.parse_args()
    report = evaluate(
        args.dataset,
        args.engine,
        include_ids=_load_ids(args.include_ids),
        exclude_ids=_load_ids(args.exclude_ids),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
