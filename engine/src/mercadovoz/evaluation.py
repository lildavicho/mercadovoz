from __future__ import annotations

import json
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .corrections import apply_correction
from .models import CORE_OPERATION_TYPES, NUMERIC_FIELDS
from .parser import parse_text


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSONL at line {line_number}: {error}") from error
    return examples


def _equal(left: Any, right: Any) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= 0.01
    return left == right


def operation_equal(predicted: dict[str, Any] | None, expected: dict[str, Any] | None) -> bool:
    if predicted is None or expected is None:
        return predicted is expected
    if set(predicted) != set(expected):
        return False
    return all(_equal(predicted[key], expected[key]) for key in expected)


def classify_errors(
    expected_envelope: dict[str, Any], predicted_envelope: dict[str, Any], metadata: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    expected_status = expected_envelope["status"]
    predicted_status = predicted_envelope["status"]
    expected = expected_envelope.get("operation") or {}
    predicted = predicted_envelope.get("operation") or {}

    if expected.get("type") != predicted.get("type"):
        errors.append("intent_incorrect")
    for field, expected_value in expected.items():
        if field == "type":
            continue
        if field not in predicted:
            errors.append(f"{field}_omitted")
        elif not _equal(predicted[field], expected_value):
            if field in NUMERIC_FIELDS:
                errors.append("number_incorrect")
            if field == "unit":
                errors.append("unit_incorrect")
            elif field == "product":
                errors.append("product_incorrect")
            elif field == "total":
                errors.append("total_incorrect")
            elif field == "customer":
                errors.append("person_incorrect")
            else:
                errors.append(f"{field}_incorrect")
    unexpected = {field for field in set(predicted) - set(expected) if predicted[field] is not None}
    if unexpected and expected_status != "COMPLETE":
        errors.append("hallucination")
    if expected_status != predicted_status:
        errors.append("abstention_incorrect")
    if metadata.get("compound") and expected_status != predicted_status:
        errors.append("compound_operation")
    if metadata.get("local_expression") and errors:
        errors.append("local_expression_not_understood")
    return sorted(set(errors))


def evaluate(examples: Iterable[dict[str, Any]], dataset_path: str | None = None) -> dict[str, Any]:
    examples = list(examples)
    intent_correct = 0
    intent_total = 0
    field_correct = 0
    field_total = 0
    exact_correct = 0
    exact_total = 0
    core_exact_correct = 0
    core_exact_total = 0
    correction_correct = 0
    correction_total = 0
    expected_abstain = 0
    predicted_abstain = 0
    correct_abstain = 0
    error_counts: Counter[str] = Counter()
    error_rows: list[dict[str, Any]] = []
    latencies_ms: list[float] = []
    per_intent: dict[str, Counter[str]] = {}

    for example in examples:
        started = time.perf_counter()
        predicted = parse_text(example["text"])
        latencies_ms.append((time.perf_counter() - started) * 1000)
        expected = example["expected"]
        expected_operation = expected.get("operation") or {}
        predicted_operation = predicted.get("operation") or {}
        expected_type = expected_operation.get("type")
        predicted_type = predicted_operation.get("type")

        if expected_type:
            intent_total += 1
            intent_correct += int(expected_type == predicted_type)
            counter = per_intent.setdefault(expected_type, Counter())
            counter["total"] += 1
            counter["intent_correct"] += int(expected_type == predicted_type)

        for field, expected_value in expected_operation.items():
            if field == "type":
                continue
            field_total += 1
            field_correct += int(field in predicted_operation and _equal(predicted_operation[field], expected_value))

        if expected["status"] == "COMPLETE":
            exact_total += 1
            exact = predicted["status"] == "COMPLETE" and operation_equal(predicted_operation, expected_operation)
            exact_correct += int(exact)
            if expected_type in CORE_OPERATION_TYPES:
                core_exact_total += 1
                core_exact_correct += int(exact)
            if expected_type:
                per_intent[expected_type]["exact_correct"] += int(exact)
                per_intent[expected_type]["exact_total"] += 1

        expected_is_abstention = expected["status"] != "COMPLETE"
        predicted_is_abstention = predicted["status"] != "COMPLETE"
        expected_abstain += int(expected_is_abstention)
        predicted_abstain += int(predicted_is_abstention)
        correct_abstain += int(expected_is_abstention and predicted_is_abstention)

        metadata = example.get("metadata") or {}
        correction_text = metadata.get("correction_text")
        expected_after = metadata.get("expected_after_correction")
        if correction_text and expected_after:
            correction_total += 1
            corrected = apply_correction(predicted, correction_text)
            correction_correct += int(
                corrected["status"] == "COMPLETE"
                and operation_equal(corrected.get("operation"), expected_after)
            )

        row_errors = classify_errors(expected, predicted, metadata)
        if row_errors:
            error_counts.update(row_errors)
            error_rows.append(
                {
                    "id": example["id"],
                    "text": example["text"],
                    "expected": expected,
                    "predicted": predicted,
                    "categories": row_errors,
                }
            )

    abstention_precision = correct_abstain / predicted_abstain if predicted_abstain else 0.0
    abstention_recall = correct_abstain / expected_abstain if expected_abstain else 0.0
    per_intent_output = {
        key: {
            "examples": value["total"],
            "intent_accuracy": value["intent_correct"] / value["total"] if value["total"] else 0.0,
            "exact_operation_accuracy": value["exact_correct"] / value["exact_total"] if value["exact_total"] else None,
        }
        for key, value in sorted(per_intent.items())
    }
    return {
        "engine": {
            "name": "deterministic-rules-baseline",
            "version": "0.1.0",
            "model": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "estimated_cost_per_100_operations_usd": 0.0,
        },
        "dataset": {"path": dataset_path, "examples": len(examples)},
        "metrics": {
            "intent_accuracy": intent_correct / intent_total if intent_total else 0.0,
            "field_accuracy": field_correct / field_total if field_total else 0.0,
            "exact_operation_accuracy": exact_correct / exact_total if exact_total else 0.0,
            "core_exact_operation_accuracy": core_exact_correct / core_exact_total if core_exact_total else 0.0,
            "confirmation_recovery": correction_correct / correction_total if correction_total else None,
            "abstention_precision": abstention_precision,
            "abstention_recall": abstention_recall,
            "counts": {
                "intent": {"correct": intent_correct, "total": intent_total},
                "fields": {"correct": field_correct, "total": field_total},
                "exact": {"correct": exact_correct, "total": exact_total},
                "core_exact": {"correct": core_exact_correct, "total": core_exact_total},
                "corrections": {"correct": correction_correct, "total": correction_total},
                "abstentions": {
                    "expected": expected_abstain,
                    "predicted": predicted_abstain,
                    "correct": correct_abstain,
                },
            },
        },
        "latency_ms": {
            "mean": statistics.mean(latencies_ms) if latencies_ms else 0.0,
            "median": statistics.median(latencies_ms) if latencies_ms else 0.0,
            "max": max(latencies_ms) if latencies_ms else 0.0,
        },
        "per_intent": per_intent_output,
        "error_counts": dict(error_counts.most_common()),
        "errors": error_rows,
    }


def evaluate_path(path: str | Path) -> dict[str, Any]:
    return evaluate(load_jsonl(path), str(path))
