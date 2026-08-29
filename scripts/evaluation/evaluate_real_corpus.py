from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from mercadovoz.evaluation import evaluate
from mercadovoz.parser import parse_text


UNKNOWN_CATEGORIES = {
    "UNKNOWN_UNIT",
    "UNKNOWN_EXPRESSION",
    "IMPLICIT_AMOUNT",
    "COMPOUND_OPERATION",
    "OUT_OF_SCOPE_INTENT",
    "AMBIGUOUS_REFERENCE",
    "IMPLICIT_REFERENCE",
    "UNEXPECTED_STRUCTURE",
    "ABBREVIATION",
    "SCHEMA_GAP",
    "PRICE_TOTAL_AMBIGUITY",
    "IMPLICIT_PRODUCT",
    "IMPLICIT_CUSTOMER",
    "MISSING_PRICE",
    "MISSING_PRODUCT",
    "MISSING_QUANTITY",
    "MISSING_AMOUNT",
    "TEMPORAL_REFERENCE",
    "ARITHMETIC_REFERENCE",
    "CONTEXT_REQUIRED",
    "STATE_VS_EVENT",
    "APPROXIMATE_AMOUNT",
    "NON_EXACT_AMOUNT",
    "NUMERIC_COORDINATION",
    "OTHER",
}
REQUIRED_FIELDS = {
    "participant_id",
    "utterance_id",
    "text_original",
    "text_anonymized",
    "context",
    "expected_status",
    "expected_operation",
    "expected_fields",
    "unknown_language_categories",
    "notes",
}
EXPECTED_STATUSES = {"COMPLETE", "NEEDS_CONFIRMATION", "UNRECOGNIZED"}


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"JSON inválido en línea {line_number}: {error}") from error
        validate_record(record, line_number)
        if record["utterance_id"] in seen_ids:
            raise ValueError(f"Línea {line_number}: utterance_id duplicado {record['utterance_id']}")
        seen_ids.add(record["utterance_id"])
        records.append(record)
    return records


def validate_record(record: dict[str, Any], line_number: int) -> None:
    missing = REQUIRED_FIELDS - set(record)
    if missing:
        raise ValueError(f"Línea {line_number}: faltan campos {sorted(missing)}")
    participant = record["participant_id"]
    utterance = record["utterance_id"]
    if not isinstance(participant, str) or not re.fullmatch(
        r"P\d{2}(?:-WEB(?:-DERIVED)?)?", participant
    ):
        raise ValueError(
            f"Línea {line_number}: participant_id debe usar P01…P99, P00-WEB o P01-WEB-DERIVED"
        )
    if not isinstance(utterance, str) or not re.fullmatch(rf"{re.escape(participant)}-\d{{3}}", utterance):
        raise ValueError(f"Línea {line_number}: utterance_id no corresponde a {participant}")
    for field in ("text_original", "text_anonymized", "context", "notes"):
        if not isinstance(record[field], str):
            raise ValueError(f"Línea {line_number}: {field} debe ser texto")
    if not record["text_anonymized"].strip():
        raise ValueError(f"Línea {line_number}: text_anonymized está vacío")
    if record["expected_status"] not in EXPECTED_STATUSES:
        raise ValueError(f"Línea {line_number}: expected_status inválido")
    operation = record["expected_operation"]
    expected_fields = record["expected_fields"]
    if operation is not None and not isinstance(operation, dict):
        raise ValueError(f"Línea {line_number}: expected_operation debe ser objeto o null")
    if not isinstance(expected_fields, list) or any(not isinstance(item, str) for item in expected_fields):
        raise ValueError(f"Línea {line_number}: expected_fields debe ser una lista de textos")
    if set(expected_fields) != set((operation or {}).keys()):
        raise ValueError(f"Línea {line_number}: expected_fields no coincide con expected_operation")
    categories = record["unknown_language_categories"]
    if not isinstance(categories, list) or not set(categories) <= UNKNOWN_CATEGORIES:
        unknown = sorted(set(categories) - UNKNOWN_CATEGORIES) if isinstance(categories, list) else categories
        raise ValueError(f"Línea {line_number}: categorías desconocidas {unknown}")
    if "source_type" in record and not isinstance(record["source_type"], str):
        raise ValueError(f"Línea {line_number}: source_type debe ser texto")
    if "real_participant" in record and not isinstance(record["real_participant"], bool):
        raise ValueError(f"Línea {line_number}: real_participant debe ser booleano")
    for field in ("real_interview", "eligible_for_final_heldout"):
        if field in record and not isinstance(record[field], bool):
            raise ValueError(f"Línea {line_number}: {field} debe ser booleano")


def to_evaluator_record(record: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "source": record.get("source_type", "REAL_ANONYMIZED"),
        "participant_id": record["participant_id"],
        "real_participant": record.get("real_participant", True),
        "real_interview": record.get("real_interview", record.get("real_participant", True)),
        "eligible_for_final_heldout": record.get("eligible_for_final_heldout", True),
        "context": record["context"],
        "unknown_language_categories": record["unknown_language_categories"],
    }
    if record.get("correction_text_anonymized") and record.get("expected_after_correction"):
        metadata["correction_text"] = record["correction_text_anonymized"]
        metadata["expected_after_correction"] = record["expected_after_correction"]
    return {
        "id": record["utterance_id"],
        "text": record["text_anonymized"],
        "expected": {
            "status": record["expected_status"],
            "operation": record["expected_operation"],
        },
        "metadata": metadata,
    }


def build_report(
    records: list[dict[str, Any]], evaluation_ids: set[str], dataset_path: Path, role: str = "heldout"
) -> dict[str, Any]:
    all_ids = {record["participant_id"] for record in records}
    missing_ids = evaluation_ids - all_ids
    if missing_ids:
        raise ValueError(f"Participantes de evaluación inexistentes: {sorted(missing_ids)}")
    selected = [record for record in records if record["participant_id"] in evaluation_ids]
    development_ids = (
        sorted(all_ids - evaluation_ids)
        if role == "heldout"
        else sorted(all_ids)
        if role == "development_pilot"
        else []
    )
    evaluation_records = [to_evaluator_record(record) for record in selected]
    report = evaluate(evaluation_records, str(dataset_path))

    predictions = [parse_text(record["text_anonymized"]) for record in selected]
    recognized = sum(prediction.get("operation") is not None for prediction in predictions)
    complete = sum(prediction["status"] == "COMPLETE" for prediction in predictions)
    unknown_counts: Counter[str] = Counter(
        category for record in selected for category in record["unknown_language_categories"]
    )
    unknown_examples = sum(bool(record["unknown_language_categories"]) for record in selected)
    total = len(selected)
    report["real_world"] = {
        "evaluation_role": role,
        "eligible_for_real_metrics": role == "heldout",
        "participants_total": len(all_ids),
        "development_participants": development_ids,
        "evaluated_participants": sorted(evaluation_ids),
        "heldout_participants": sorted(evaluation_ids) if role == "heldout" else [],
        "utterances_total": len(records),
        "evaluated_utterances": total,
        "recognition_coverage": recognized / total if total else 0.0,
        "complete_coverage": complete / total if total else 0.0,
        "unknown_language_rate": unknown_examples / total if total else 0.0,
        "unknown_language_counts": dict(sorted(unknown_counts.items())),
    }
    report["case_results"] = [
        {
            "id": record["utterance_id"],
            "text": record["text_anonymized"],
            "expected": {
                "status": record["expected_status"],
                "operation": record["expected_operation"],
            },
            "predicted": prediction,
            "unknown_language_categories": record["unknown_language_categories"],
        }
        for record, prediction in zip(selected, predictions)
    ]
    repo_root = Path(__file__).resolve().parents[2]
    synthetic_path = repo_root / "research" / "benchmarks" / "results" / "heldout-rules.json"
    synthetic = json.loads(synthetic_path.read_text(encoding="utf-8"))
    synthetic_metrics = synthetic["metrics"]
    report["synthetic_reference"] = {
        "path": str(synthetic_path),
        "intent_accuracy": synthetic_metrics["intent_accuracy"],
        "field_accuracy": synthetic_metrics["field_accuracy"],
        "exact_operation_accuracy": synthetic_metrics["exact_operation_accuracy"],
        "core_exact_operation_accuracy": synthetic_metrics["core_exact_operation_accuracy"],
        "confirmation_recovery": synthetic_metrics["confirmation_recovery"],
        "abstention_precision": synthetic_metrics["abstention_precision"],
        "abstention_recall": synthetic_metrics["abstention_recall"],
    }
    report["comparison_percentage_points"] = {
        metric: round((report["metrics"][metric] - synthetic_metrics[metric]) * 100, 2)
        if report["metrics"][metric] is not None and synthetic_metrics[metric] is not None
        else None
        for metric in (
            "intent_accuracy",
            "field_accuracy",
            "exact_operation_accuracy",
            "core_exact_operation_accuracy",
            "confirmation_recovery",
            "abstention_precision",
            "abstention_recall",
        )
    }
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Valida y evalúa corpus real sin modificar MercadoVoz baseline v0")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--validate-only", action="store_true", help="Valida estructura sin ejecutar el parser")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--heldout-participants", nargs="+", default=[])
    selection.add_argument("--development-pilot", metavar="PARTICIPANT_ID")
    selection.add_argument("--exploratory-corpus", metavar="CORPUS_ID")
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        records = load_records(args.dataset)
        participants = sorted({record["participant_id"] for record in records})
        if args.validate_only:
            print(f"Registros válidos: {len(records)}; participantes: {len(participants)}")
            return 0
        if args.development_pilot:
            report = build_report(records, {args.development_pilot}, args.dataset, role="development_pilot")
            if report["dataset"]["examples"] == 0:
                raise ValueError(f"No hay frases para {args.development_pilot}")
            output_path = args.output or Path(f"data/private/{args.development_pilot.lower()}-baseline-v0.json")
        elif args.exploratory_corpus:
            report = build_report(records, {args.exploratory_corpus}, args.dataset, role="exploratory_web")
            if report["dataset"]["examples"] == 0:
                raise ValueError(f"No hay frases para {args.exploratory_corpus}")
            output_path = args.output or Path(
                f"data/private/{args.exploratory_corpus.lower()}-baseline-v0.json"
            )
        else:
            if len(records) < 50 or not 6 <= len(participants) <= 8:
                raise ValueError("La evaluación held-out requiere al menos 50 frases y entre 6 y 8 participantes")
            heldout_ids = set(args.heldout_participants)
            if len(heldout_ids) != 2:
                raise ValueError("Seleccione exactamente dos participantes held-out completos")
            report = build_report(records, heldout_ids, args.dataset)
            output_path = args.output or Path("data/private/real-baseline-v0.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"metrics": report["metrics"], "real_world": report["real_world"]}, ensure_ascii=False, indent=2))
        print(f"Resultado guardado: {output_path}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
