import unittest
from pathlib import Path

from mercadovoz.evaluation import evaluate, load_jsonl


ROOT = Path(__file__).resolve().parents[2]


class EvaluationTests(unittest.TestCase):
    def test_dataset_and_metrics_are_reproducible(self):
        cases = load_jsonl(ROOT / "research" / "benchmarks" / "synthetic" / "development.jsonl")
        self.assertEqual(40, len(cases))
        report = evaluate(cases)
        self.assertEqual(40, report["dataset"]["examples"])
        for name in (
            "intent_accuracy",
            "field_accuracy",
            "exact_operation_accuracy",
            "core_exact_operation_accuracy",
        ):
            self.assertGreaterEqual(report["metrics"][name], 0)
            self.assertLessEqual(report["metrics"][name], 1)


if __name__ == "__main__":
    unittest.main()
