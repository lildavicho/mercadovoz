"""Replay a frozen private round with a new engine without changing original evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from mercadovoz_core import MercadoVozEngine


PRONOUNS = {"me", "te", "le", "lo", "la", "nos", "les", "se", "el", "ella"}


def critical_violation(text: str, prediction: dict[str, Any]) -> str | None:
    operation = prediction.get("operation") or {}
    status = prediction.get("status")
    normalized = prediction.get("normalized_text", "")
    if operation.get("customer", "").casefold() in PRONOUNS:
        return "pronoun_as_customer"
    if re.search(r"\b(?:como|aproximadamente|aprox|casi|unos|unas|mas o menos)\b", normalized) and operation:
        return "approximation_made_exact"
    if re.search(r"\b(?:todavia|aun|sigue)\b.*\b(?:debe|debiendo)\b", normalized) and operation.get("type") == "RECEIVABLE":
        return "existing_debt_duplicated"
    if status == "COMPOUND_OPERATION" and operation:
        return "compound_operation_proposed"
    for field in ("amount", "quantity", "unit_price", "total"):
        value = operation.get(field)
        if value is None:
            continue
        number = float(value)
        if not math.isfinite(number) or number <= 0:
            return f"invalid_numeric_{field}"
    if operation.get("quantity") is not None and operation.get("unit_price") is not None:
        expected = float(operation["quantity"]) * float(operation["unit_price"])
        if operation.get("total") is None or abs(float(operation["total"]) - expected) > 0.01:
            return "inconsistent_total"
    return None


def comparison(record: dict[str, Any], new: dict[str, Any]) -> str:
    old = record.get("initial_prediction")
    new_operation = new.get("operation")
    accepted = record.get("expected_or_final_accepted_operation")
    if accepted and new_operation != accepted:
        return "regressed"
    if accepted and new_operation == accepted:
        return "same" if old == new_operation else "improved"
    if old == new_operation:
        return "same"
    if (
        old
        and old.get("type") == "RECEIVABLE"
        and not old.get("customer")
        and (new_operation or {}).get("customer")
        and new.get("status") == "COMPLETE"
    ):
        return "improved"
    if (
        old
        and old.get("type") == "SALE"
        and old.get("total") is not None
        and not old.get("unit_price")
        and new_operation == {**old, "unit_price": None}
        and new.get("status") == "COMPLETE"
    ):
        return "improved"
    old_product = str((old or {}).get("product", "")).casefold()
    new_product = str((new_operation or {}).get("product", "")).casefold()
    if old_product and new_product and len(new_product) < len(old_product) and any(
        marker in old_product for marker in (" cada ", " en total", " centavos", " dolares")
    ):
        return "improved_known_boundary"
    if (old or {}).get("customer", "").casefold() in PRONOUNS and not (new_operation or {}).get("customer"):
        return "safer_pronoun_removed"
    if old and not new_operation and new.get("status") in {
        "AMBIGUOUS", "COMPOUND_OPERATION", "OUT_OF_SCOPE", "UNSAFE", "UNRECOGNIZED"
    }:
        return "safer_abstention"
    return "changed_without_ground_truth"


def replay(
    source: Path,
    output: Path,
    *,
    source_round_id: str,
    source_engine_version: str,
    replay_engine_version: str,
) -> dict[str, Any]:
    engine = MercadoVozEngine()
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    cases: list[dict[str, Any]] = []
    classes: Counter[str] = Counter()
    violations: Counter[str] = Counter()
    for record in records:
        prediction = engine.interpret(record["original_text"])
        category = comparison(record, prediction)
        violation = critical_violation(record["original_text"], prediction)
        classes[category] += 1
        if violation:
            violations[violation] += 1
        cases.append({
            "record_id": record["record_id"],
            "round_id": record["round_id"],
            "original_text": record["original_text"],
            "historical": {
                "interpretation_state": record.get("initial_interpretation_state"),
                "operation": record.get("initial_prediction"),
                "warnings": record.get("warnings", []),
            },
            "replay": prediction,
            "comparison": category,
            "critical_financial_violation": violation,
            "ground_truth_available": record.get("ground_truth_status") == "USER_ACCEPTED_OPERATION",
        })
    report = {
        "source_dataset_class": "REAL_DEVELOPMENT",
        "source_round_id": source_round_id,
        "source_engine_version": source_engine_version,
        "replay_engine_version": replay_engine_version,
        "replay_is_new_field_evidence": False,
        "accuracy": "NOT_MEASURABLE",
        "records": len(records),
        "comparison_counts": dict(sorted(classes.items())),
        "critical_financial_violations": sum(violations.values()),
        "critical_violation_types": dict(sorted(violations.items())),
        "cases": cases,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"output": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), **{k: report[k] for k in (
        "records", "comparison_counts", "critical_financial_violations", "critical_violation_types"
    )}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-round", required=True)
    parser.add_argument("--source-engine", required=True)
    parser.add_argument("--replay-engine", required=True)
    args = parser.parse_args()
    print(json.dumps(replay(
        args.source,
        args.output,
        source_round_id=args.source_round,
        source_engine_version=args.source_engine,
        replay_engine_version=args.replay_engine,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
