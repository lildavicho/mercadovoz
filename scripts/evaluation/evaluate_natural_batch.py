#!/usr/bin/env python3
"""Evaluate the manually authored natural batch development corpus."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine/src"))

from mercadovoz.numbers import strip_accents  # noqa: E402
from mercadovoz_batch.interpreter import BatchInterpreter  # noqa: E402


def rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def locate_spans(text: str, segments: list[dict[str, Any]]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = 0
    for segment in segments:
        source = segment["text"]
        start = text.find(source, cursor)
        if start < 0:
            raise ValueError(f"annotated segment is not a sequential source span: {source!r}")
        end = start + len(source)
        spans.append((start, end))
        cursor = end
    return spans


def predicted_by_span(result: dict[str, Any]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for item in result["segments"]:
        span = (item["source_span"]["start"], item["source_span"]["end"])
        grouped.setdefault(span, []).append(item)
    return grouped


def span_type(items: list[dict[str, Any]], groups: list[dict[str, Any]]) -> str | None:
    item_ids = {item["segment_id"] for item in items}
    for group in groups:
        if item_ids and item_ids.issubset(set(group.get("related_segment_ids", []))):
            return f"GROUP:{group['type']}"
    operations = [item.get("operation", {}).get("type") for item in items if item.get("operation")]
    return operations[0] if len(operations) == 1 else None


def evaluate(path: Path) -> dict[str, Any]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if len(cases) < 100:
        raise ValueError("manual natural corpus must contain at least 100 narratives")
    if len({case["text"] for case in cases}) != len(cases):
        raise ValueError("manual natural corpus contains duplicate narratives")

    engine = BatchInterpreter()
    boundary_tp = boundary_fp = boundary_fn = 0
    exact_segment_counts = exact_batches = 0
    expected_operations = correct_intents = 0
    expected_fields = correct_fields = 0
    source_span_integrity = 0
    partial_cases = safe_partial_cases = 0
    unsafe_merges = customer_crossovers = amount_crossovers = critical = 0
    latencies: list[float] = []
    statuses: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []

    for case in cases:
        text = case["text"]
        gold_segments = case["segments"]
        gold_spans = locate_spans(text, gold_segments)
        result = engine.interpret(text)
        latencies.append(float(result["latency_ms"]))
        statuses[result["status"]] += 1
        predicted = predicted_by_span(result)
        predicted_spans = set(predicted)
        gold_span_set = set(gold_spans)
        boundary_tp += len(predicted_spans & gold_span_set)
        boundary_fp += len(predicted_spans - gold_span_set)
        boundary_fn += len(gold_span_set - predicted_spans)
        exact_segment_counts += int(predicted_spans == gold_span_set)

        internally_valid = all(
            text[start:end] == item["source_text"]
            for item in result["segments"]
            for start, end in [(item["source_span"]["start"], item["source_span"]["end"])]
        )
        source_span_integrity += int(internally_valid)
        if not internally_valid:
            critical += 1

        expected_types: list[str | None] = []
        predicted_types: list[str | None] = []
        has_safe = has_blocked = recovered_safe = unsafe_blocked = False
        for gold, span in zip(gold_segments, gold_spans, strict=True):
            items = predicted.get(span, [])
            predicted_type = span_type(items, result.get("groups", [])) if items else None
            expected_type = gold.get("type")
            expected_types.append(expected_type)
            predicted_types.append(predicted_type)
            confirmable = any(item.get("confirmable") for item in items)
            if expected_type is None:
                has_blocked = True
                unsafe_blocked |= confirmable
                if confirmable:
                    critical += 1
            else:
                has_safe = True
                expected_operations += 1
                correct_intents += int(predicted_type == expected_type)
                recovered_safe |= predicted_type == expected_type and confirmable

            operation = next((item.get("operation") for item in items if item.get("operation")), None)
            group = None
            if expected_type and expected_type.startswith("GROUP:"):
                group_name = expected_type.removeprefix("GROUP:")
                item_ids = {item["segment_id"] for item in items}
                group = next((
                    value for value in result.get("groups", [])
                    if value.get("type") == group_name
                    and item_ids.issubset(set(value.get("related_segment_ids", [])))
                ), None)
            observed = group or operation or {}
            for field, expected in gold.get("fields", {}).items():
                expected_fields += 1
                actual = observed.get(field)
                correct_fields += int(actual == expected)
                names_match = (
                    field == "customer"
                    and actual is not None
                    and strip_accents(str(actual).casefold()) == strip_accents(str(expected).casefold())
                )
                if field == "customer" and actual not in (None, expected) and not names_match:
                    customer_crossovers += 1
                    critical += 1
                if field in {"amount", "total", "unit_price"} and actual not in (None, expected):
                    amount_crossovers += 1
                    critical += 1

        if has_safe and has_blocked:
            partial_cases += 1
            safe_partial_cases += int(recovered_safe and not unsafe_blocked)
        exact_batches += int(expected_types == predicted_types)

        for span in predicted_spans - gold_span_set:
            if sum(1 for gold_span in gold_spans if span[0] <= gold_span[0] and span[1] >= gold_span[1]) > 1:
                unsafe_merges += 1
                if any(item.get("confirmable") for item in predicted[span]):
                    critical += 1

        if len(errors) < 30 and expected_types != predicted_types:
            errors.append({
                "id": case["id"],
                "expected": expected_types,
                "predicted": predicted_types,
                "status": result["status"],
            })

    return {
        "engine_version": "1.2.0",
        "dataset_class": "MANUAL_NATURAL_BATCH_DEVELOPMENT",
        "dataset": str(path.relative_to(ROOT)),
        "examples": len(cases),
        "expected_operations": expected_operations,
        "annotated_fields": expected_fields,
        "metrics": {
            "exact_segment_count_rate": rate(exact_segment_counts, len(cases)),
            "boundary_precision": rate(boundary_tp, boundary_tp + boundary_fp),
            "boundary_recall": rate(boundary_tp, boundary_tp + boundary_fn),
            "intent_accuracy_per_item": rate(correct_intents, expected_operations),
            "field_accuracy": rate(correct_fields, expected_fields),
            "batch_exact_match_rate": rate(exact_batches, len(cases)),
            "safe_partial_recovery_rate": rate(safe_partial_cases, partial_cases),
            "unsafe_merge_rate": rate(unsafe_merges, sum(len(case["segments"]) for case in cases)),
            "customer_cross_contamination": customer_crossovers,
            "amount_cross_contamination": amount_crossovers,
            "source_span_integrity_rate": rate(source_span_integrity, len(cases)),
            "critical_financial_violations": critical,
            "median_latency_ms": round(statistics.median(latencies), 3),
            "p95_latency_ms": round(sorted(latencies)[int((len(latencies) - 1) * 0.95)], 3),
        },
        "statuses": dict(sorted(statuses.items())),
        "error_sample": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    report = evaluate(arguments.dataset.resolve())
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
