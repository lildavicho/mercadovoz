#!/usr/bin/env python3
"""Evaluate Engine 1.2 batch boundaries, operations, safety, and latency."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine/src"))

from mercadovoz_batch.interpreter import BatchInterpreter  # noqa: E402


def rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * fraction))]


def evaluate(path: Path) -> dict:
    engine = BatchInterpreter()
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    exact_boundaries = 0
    expected_operations = 0
    recovered_operations = 0
    exact_batches = 0
    safe_spans = 0
    partial_recovery = 0
    critical_violations = 0
    latencies: list[float] = []
    states: dict[str, int] = {}
    errors: list[dict] = []
    for case in cases:
        result = engine.interpret(case["text"])
        latencies.append(result["latency_ms"])
        states[result["status"]] = states.get(result["status"], 0) + 1
        spans_valid = all(
            case["text"][item["source_span"]["start"]:item["source_span"]["end"]] == item["source_text"]
            for item in result["segments"]
        )
        safe_spans += int(spans_valid)
        expected_count = case["expected_segment_count"]
        exact_boundaries += int(len(result["segments"]) == expected_count)
        expected = case["expected_operation_types"]
        predicted = [item["operation"]["type"] for item in result["segments"] if item.get("operation")]
        expected_operations += len(expected)
        matched = sum(1 for offset, operation in enumerate(expected) if offset < len(predicted) and predicted[offset] == operation)
        recovered_operations += matched
        exact_batches += int(predicted == expected)
        partial_recovery += int(0 < matched < len(expected))
        for item in result["segments"]:
            operation = item.get("operation") or {}
            monetary = operation.get("total", operation.get("amount"))
            if item.get("confirmable") and (not operation.get("type") or monetary is None or monetary <= 0):
                critical_violations += 1
        if len(errors) < 25 and (len(result["segments"]) != expected_count or predicted != expected):
            errors.append({"id": case["id"], "expected": expected, "predicted": predicted, "status": result["status"]})
    return {
        "engine_version": "1.2.0",
        "dataset": str(path.relative_to(ROOT)),
        "examples": len(cases),
        "expected_operations": expected_operations,
        "metrics": {
            "exact_segment_count_rate": rate(exact_boundaries, len(cases)),
            "source_span_integrity_rate": rate(safe_spans, len(cases)),
            "operation_recall": rate(recovered_operations, expected_operations),
            "batch_exact_match_rate": rate(exact_batches, len(cases)),
            "partial_recovery_rate": rate(partial_recovery, len(cases)),
            "critical_financial_violations": critical_violations,
            "median_latency_ms": round(statistics.median(latencies), 3),
            "p95_latency_ms": round(percentile(latencies, 0.95), 3),
        },
        "statuses": states,
        "error_sample": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(args.dataset.resolve())
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
