from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_batch_engine", ROOT / "scripts/evaluation/evaluate_batch_engine.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class BatchEvaluationTests(unittest.TestCase):
    def test_versioned_benchmark_is_reproducible_and_financially_safe(self) -> None:
        path = ROOT / "research/benchmarks/batch/synthetic-batch-v1.jsonl"
        first = MODULE.evaluate(path)
        second = MODULE.evaluate(path)
        self.assertEqual(first["examples"], 3000)
        self.assertEqual(first["metrics"]["critical_financial_violations"], 0)
        for key in ("exact_segment_count_rate", "source_span_integrity_rate", "operation_recall", "field_accuracy", "batch_exact_match_rate"):
            self.assertEqual(first["metrics"][key], second["metrics"][key])


if __name__ == "__main__":
    unittest.main()
