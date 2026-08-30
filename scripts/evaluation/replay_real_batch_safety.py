#!/usr/bin/env python3
"""Replay a private frozen JSONL through batch sidecar and print aggregates only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine/src"))

from mercadovoz_batch.interpreter import BatchInterpreter  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    engine = BatchInterpreter()
    records = [json.loads(line) for line in args.dataset.read_text(encoding="utf-8").splitlines() if line]
    statuses: dict[str, int] = {}
    invalid_confirmable = 0
    span_failures = 0
    for record in records:
        text = record["original_text"]
        result = engine.interpret(text, input_mode="TEXT_SINGLE")
        statuses[result["status"]] = statuses.get(result["status"], 0) + 1
        for item in result["segments"]:
            span = item["source_span"]
            span_failures += int(text[span["start"]:span["end"]] != item["source_text"])
            operation = item.get("operation") or {}
            monetary = operation.get("total", operation.get("amount"))
            invalid_confirmable += int(item["confirmable"] and (not operation.get("type") or monetary is None or monetary <= 0))
    print(json.dumps({
        "records": len(records),
        "engine_version": "1.2.0",
        "ground_truth_evaluated": False,
        "statuses": statuses,
        "span_failures": span_failures,
        "invalid_confirmable_operations": invalid_confirmable,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
