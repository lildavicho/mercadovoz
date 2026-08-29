from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any

from mercadovoz_core import MercadoVozEngine


CORE_TYPES = {"SALE", "EXPENSE", "RECEIVABLE", "PAYMENT_RECEIVED"}
SAFE_NONFINAL = {
    "NEEDS_CONFIRMATION",
    "NEEDS_CONTEXT",
    "AMBIGUOUS",
    "COMPOUND_OPERATION",
    "OUT_OF_SCOPE",
    "UNSAFE",
    "UNRECOGNIZED",
}


def load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def canonical_case(row: dict[str, Any]) -> dict[str, Any]:
    if "expected" in row:
        expected = row["expected"]
        return {
            "id": row["id"],
            "text": row["text"],
            "expected_status": expected["status"],
            "expected_operation": expected.get("operation"),
            "expected_fields": list((expected.get("operation") or {}).keys()),
            "categories": row.get("metadata", {}).get("categories", []),
        }
    return {
        "id": row["utterance_id"],
        "text": row["text_anonymized"],
        "expected_status": row["expected_status"],
        "expected_operation": row.get("expected_operation"),
        "expected_fields": row.get("expected_fields", []),
        "categories": row.get("unknown_language_categories", []),
    }


def ratio(correct: int, total: int) -> float | None:
    return correct / total if total else None


def evaluate(path: Path, role: str) -> dict[str, Any]:
    engine = MercadoVozEngine()
    cases = [canonical_case(row) for row in load_cases(path)]
    status_correct = intent_correct = intent_total = 0
    field_correct = field_total = 0
    exact_correct = exact_total = 0
    core_exact_correct = core_exact_total = 0
    safe_correct = safe_total = 0
    unsafe_proposals = 0
    compound_correct = compound_total = 0
    context_safe = context_total = 0
    latencies: list[float] = []
    status_counts: Counter[str] = Counter()
    results: list[dict[str, Any]] = []

    for case in cases:
        started = time.perf_counter()
        predicted = engine.interpret(case["text"])
        latencies.append((time.perf_counter() - started) * 1000)
        expected_operation = case["expected_operation"]
        predicted_operation = predicted.get("operation")
        status_counts[predicted["status"]] += 1
        status_correct += predicted["status"] == case["expected_status"]

        if expected_operation and expected_operation.get("type"):
            intent_total += 1
            intent_correct += bool(
                predicted_operation
                and predicted_operation.get("type") == expected_operation["type"]
            )
            fields = [field for field in case["expected_fields"] if field != "type"]
            for field in fields:
                field_total += 1
                field_correct += bool(
                    predicted_operation and predicted_operation.get(field) == expected_operation.get(field)
                )

        if case["expected_status"] == "COMPLETE" and expected_operation:
            exact_total += 1
            is_exact = predicted_operation == expected_operation and predicted["status"] == "COMPLETE"
            exact_correct += is_exact
            if expected_operation.get("type") in CORE_TYPES:
                core_exact_total += 1
                core_exact_correct += is_exact

        should_be_nonfinal = expected_operation is None or case["expected_status"] != "COMPLETE"
        if should_be_nonfinal:
            safe_total += 1
            safe_correct += predicted["status"] in SAFE_NONFINAL
        if expected_operation is None and predicted_operation is not None:
            unsafe_proposals += 1

        if "COMPOUND_OPERATION" in case["categories"]:
            compound_total += 1
            compound_correct += predicted["status"] == "COMPOUND_OPERATION" and predicted_operation is None
        if "CONTEXT_REQUIRED" in case["categories"]:
            context_total += 1
            context_safe += predicted["status"] != "COMPLETE"

        results.append(
            {
                "id": case["id"],
                "text": case["text"],
                "expected": {
                    "status": case["expected_status"],
                    "operation": expected_operation,
                    "categories": case["categories"],
                },
                "predicted": predicted,
            }
        )

    return {
        "engine": {
            "name": "rules-context-confirmation",
            "version": engine.parser_version,
            "model": None,
            "estimated_cost_usd": 0.0,
        },
        "dataset": {"path": str(path), "role": role, "examples": len(cases)},
        "metrics": {
            "status_exact_match": ratio(status_correct, len(cases)),
            "intent_accuracy": ratio(intent_correct, intent_total),
            "expected_field_accuracy": ratio(field_correct, field_total),
            "exact_complete_accuracy": ratio(exact_correct, exact_total),
            "core_exact_complete_accuracy": ratio(core_exact_correct, core_exact_total),
            "safe_nonfinal_handling": ratio(safe_correct, safe_total),
            "unsafe_operation_proposals": unsafe_proposals,
            "compound_detection": ratio(compound_correct, compound_total),
            "context_case_safe_handling": ratio(context_safe, context_total),
            "counts": {
                "status": {"correct": status_correct, "total": len(cases)},
                "intent": {"correct": intent_correct, "total": intent_total},
                "fields": {"correct": field_correct, "total": field_total},
                "exact_complete": {"correct": exact_correct, "total": exact_total},
                "core_exact_complete": {"correct": core_exact_correct, "total": core_exact_total},
                "safe_nonfinal": {"correct": safe_correct, "total": safe_total},
                "compound": {"correct": compound_correct, "total": compound_total},
                "context": {"correct": context_safe, "total": context_total},
            },
            "predicted_statuses": dict(sorted(status_counts.items())),
        },
        "latency_ms": {
            "mean": statistics.mean(latencies) if latencies else 0,
            "median": statistics.median(latencies) if latencies else 0,
            "max": max(latencies, default=0),
        },
        "case_results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--role", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.dataset, args.role)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
