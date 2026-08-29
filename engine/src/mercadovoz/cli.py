from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .corrections import apply_correction
from .evaluation import evaluate_path
from .parser import parse_text


def _print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _summary(result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    latency = result["latency_ms"]
    engine = result["engine"]
    print(f"Examples: {result['dataset']['examples']}")
    print(f"Intent accuracy: {metrics['intent_accuracy']:.1%}")
    print(f"Field accuracy: {metrics['field_accuracy']:.1%}")
    print(f"Exact operation accuracy: {metrics['exact_operation_accuracy']:.1%}")
    print(f"Core exact operation accuracy: {metrics['core_exact_operation_accuracy']:.1%}")
    recovery = metrics["confirmation_recovery"]
    print(f"Confirmation recovery: {recovery:.1%}" if recovery is not None else "Confirmation recovery: n/a")
    print(f"Abstention precision: {metrics['abstention_precision']:.1%}")
    print(f"Abstention recall: {metrics['abstention_recall']:.1%}")
    print(f"Mean latency: {latency['mean']:.3f} ms")
    print(f"Estimated cost / 100 operations: ${engine['estimated_cost_per_100_operations_usd']:.6f}")
    print("Errors:")
    if result["error_counts"]:
        for category, count in result["error_counts"].items():
            print(f"  {category}: {count}")
    else:
        print("  none")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mercadovoz", description="MercadoVoz Sprint 0 parser lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_command = subparsers.add_parser("parse", help="Parse one commercial phrase")
    parse_command.add_argument("text")

    eval_command = subparsers.add_parser("eval", help="Evaluate a JSONL dataset")
    eval_command.add_argument("dataset")
    eval_command.add_argument("--output", help="Write the full JSON result")

    correct_command = subparsers.add_parser("correct", help="Apply a controlled correction to a parse result")
    correct_command.add_argument("result_json", help="Path to JSON produced by parse")
    correct_command.add_argument("text", help="Controlled correction, e.g. 'No, eran seis'")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "parse":
        _print_json(parse_text(args.text))
        return 0
    if args.command == "eval":
        result = evaluate_path(args.dataset)
        _summary(result)
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Full result: {output_path}")
        return 0
    if args.command == "correct":
        path = Path(args.result_json)
        result = json.loads(path.read_text(encoding="utf-8"))
        _print_json(apply_correction(result, args.text))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())

