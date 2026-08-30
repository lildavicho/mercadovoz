#!/usr/bin/env python3
"""Create deterministic, versioned batch benchmarks without participant data."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_PATH = ROOT / "research/benchmarks/batch/synthetic-batch-v1.jsonl"
EXTERNAL_PATH = ROOT / "research/benchmarks/batch/web-derived-batch-v1.jsonl"
VOICE_PATH = ROOT / "research/benchmarks/voice/numeric-risk-v1.jsonl"
SOURCE_PATH = ROOT / "research/external-cuenca-v1/mercadovoz_cuenca_external_corpus_v1.jsonl"

NAMES = ("María", "Rosa", "Ana", "Luis", "Pedro")
PRODUCTS = ("panes", "tomates", "colas", "leche", "arroz")
CONNECTORS = ("; ", ". ", " y ", ", luego ", "\n")


def write_jsonl(path: Path, records: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)
    path.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def synthetic_records(size: int, seed: int) -> list[dict]:
    randomizer = random.Random(seed)
    records: list[dict] = []
    sizes = (2, 3, 5, 10, 20)
    for index in range(size):
        count = sizes[index % len(sizes)]
        clauses: list[str] = []
        operations: list[str] = []
        expected_fields: list[dict] = []
        for ordinal in range(count):
            kind = (index + ordinal) % 3
            amount = 1 + ((index * 7 + ordinal * 3) % 19)
            if kind == 0:
                quantity = 1 + ((index + ordinal) % 7)
                price = 1 + ((index + ordinal * 2) % 5)
                clauses.append(f"Vendí {quantity} {PRODUCTS[(index + ordinal) % len(PRODUCTS)]} a {price} dólares cada uno")
                operations.append("SALE")
                expected_fields.append({"product": PRODUCTS[(index + ordinal) % len(PRODUCTS)], "quantity": quantity, "unit_price": price, "total": quantity * price})
            elif kind == 1:
                clauses.append(f"Gasté {amount} en transporte")
                operations.append("EXPENSE")
                expected_fields.append({"amount": amount, "category": "transporte"})
            else:
                clauses.append(f"{NAMES[(index + ordinal) % len(NAMES)]} quedó debiendo {amount} dólares")
                operations.append("RECEIVABLE")
                expected_fields.append({"customer": NAMES[(index + ordinal) % len(NAMES)], "amount": amount})
        connector = CONNECTORS[randomizer.randrange(len(CONNECTORS))]
        text = connector.join(clauses)
        records.append({
            "id": f"SYN-BATCH-{index + 1:04d}",
            "text": text,
            "provenance_type": "SYNTHETIC_BATCH",
            "seed": seed,
            "expected_segment_count": count,
            "expected_operation_types": operations,
            "expected_fields": expected_fields,
            "critical_financial_error_expected": False,
        })
    return records


def external_records(size: int) -> list[dict]:
    source = [json.loads(line) for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines() if line]
    records: list[dict] = []
    for index in range(size):
        first = source[(index * 2) % len(source)]
        second = source[(index * 2 + 1) % len(source)]
        records.append({
            "id": f"WEB-BATCH-{index + 1:03d}",
            "text": f"{first['text']}; {second['text']}",
            "provenance_type": "WEB_DERIVED_BATCH_COMPOSITION",
            "natural_batch_narrative": False,
            "source_record_ids": [first["id"], second["id"]],
            "source_ids": [first["source_id"], second["source_id"]],
            "expected_segment_count": 2,
            "expected_operation_types": [first["expected_operation"], second["expected_operation"]],
            "expected_fields": [first.get("expected", {}), second.get("expected", {})],
            "notes": "Composición para estrés de límites; no es habla real ni evidencia de demanda.",
        })
    return records


def voice_numeric_records() -> list[dict]:
    pairs = (
        ("quince", "cincuenta"), ("dieciséis", "sesenta"),
        ("trece", "treinta"), ("catorce", "cuarenta"),
        ("diecisiete", "setenta"), ("dieciocho", "ochenta"),
        ("diecinueve", "noventa"), ("dos", "doce"),
        ("cinco dólares", "cincuenta dólares"), ("cinco con cincuenta", "cincuenta y cinco"),
    )
    templates = (
        "Vendí producto por {value}",
        "Gasté {value} en transporte",
        "María quedó debiendo {value}",
        "María me pagó {value}",
        "Vendí dos unidades a {value} cada una",
    )
    records: list[dict] = []
    for pair_index, (target, confusable) in enumerate(pairs, start=1):
        for template_index, template in enumerate(templates, start=1):
            records.append({
                "id": f"VOICE-NUM-{pair_index:02d}-{template_index}",
                "reference_text": template.format(value=target),
                "critical_confusable_text": template.format(value=confusable),
                "locale": "es-EC",
                "provenance_type": "SYNTHETIC_VOICE_NUMERIC_RISK",
                "requires_audio": True,
                "metric": "critical_numeric_token_substitution",
            })
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-size", type=int, default=3000)
    parser.add_argument("--external-size", type=int, default=60)
    parser.add_argument("--seed", type=int, default=12012026)
    args = parser.parse_args()
    synthetic = synthetic_records(args.synthetic_size, args.seed)
    external = external_records(args.external_size)
    voice = voice_numeric_records()
    manifest = {
        "schema_version": "batch-benchmark-v1",
        "seed": args.seed,
        "datasets": {
            str(SYNTHETIC_PATH.relative_to(ROOT)): {
                "records": len(synthetic), "sha256": write_jsonl(SYNTHETIC_PATH, synthetic),
            },
            str(EXTERNAL_PATH.relative_to(ROOT)): {
                "records": len(external), "sha256": write_jsonl(EXTERNAL_PATH, external),
            },
            str(VOICE_PATH.relative_to(ROOT)): {
                "records": len(voice), "sha256": write_jsonl(VOICE_PATH, voice),
            },
        },
    }
    manifest_path = ROOT / "research/benchmarks/batch/manifest-v1.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
