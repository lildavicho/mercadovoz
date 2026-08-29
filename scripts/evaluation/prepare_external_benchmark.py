from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from mercadovoz.numbers import replace_number_words


SEED = "external-cuenca-v1-family-split"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def plain(text: str) -> str:
    value = "".join(
        char
        for char in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(char) != "Mn"
    )
    value = replace_number_words(value)
    value = re.sub(r"\[[^\]]+\]", " <persona> ", value)
    value = re.sub(r"\d+(?:[.,]\d+)?", " <num> ", value)
    value = re.sub(r"[^a-zñ<>\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def family_key(row: dict[str, Any]) -> str:
    skeleton = plain(row["text"])
    expected = row.get("expected") or {}
    for field in ("customer", "product", "category", "unit"):
        value = expected.get(field)
        if isinstance(value, str) and value:
            normalized = plain(value)
            skeleton = re.sub(rf"\b{re.escape(normalized)}\b", f"<{field}>", skeleton)
    return f"{row['phenomenon']}|{skeleton}"


def stable_rank(value: str) -> str:
    return hashlib.sha256(f"{SEED}|{value}".encode()).hexdigest()


def split(rows: list[dict[str, Any]]) -> tuple[list[str], list[str], dict[str, str]]:
    by_phenomenon: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    keys: dict[str, str] = {}
    for row in rows:
        structural_key = family_key(row)
        # Source is part of the allocation group: this keeps template/source
        # clusters together while avoiding a single cross-source template
        # consuming most of heldout.
        allocation_key = f"{row['source_id']}|{structural_key}"
        keys[row["id"]] = allocation_key
        by_phenomenon[row["phenomenon"]][allocation_key].append(row)

    heldout: set[str] = set()
    for phenomenon, families in sorted(by_phenomenon.items()):
        target = max(1, round(sum(len(group) for group in families.values()) * 0.25))
        selected = 0
        ordered = sorted(families.items(), key=lambda item: stable_rank(f"{phenomenon}|{item[0]}"))
        for key, group in ordered:
            if selected >= target:
                break
            # Keep source/template groups complete and choose only additions
            # that move the phenomenon closer to its 25% target.
            if abs(target - (selected + len(group))) <= abs(target - selected):
                heldout.update(row["id"] for row in group)
                selected += len(group)
        # A phenomenon with a single oversized cluster cannot be split without
        # structural leakage; leave it in development and record zero heldout.
    dev = [row["id"] for row in rows if row["id"] not in heldout]
    held = [row["id"] for row in rows if row["id"] in heldout]
    return dev, held, keys


def prior_texts(root: Path) -> list[dict[str, str]]:
    sources = [
        ("synthetic_development", root / "research/benchmarks/synthetic/development.jsonl", "text"),
        ("synthetic_heldout", root / "research/benchmarks/synthetic/evaluation.jsonl", "text"),
        ("p00_web", root / "research/benchmarks/web-derived/P00_WEB_CORPUS.jsonl", "text_anonymized"),
        ("p01_web_derived", root / "research/benchmarks/web-derived/P01_WEB_DERIVED_CORPUS.jsonl", "text_anonymized"),
    ]
    records: list[dict[str, str]] = []
    for corpus, path, field in sources:
        for row in load_jsonl(path):
            records.append(
                {
                    "corpus": corpus,
                    "id": str(row.get("id") or row.get("utterance_id")),
                    "text": row[field],
                    "normalized": plain(row[field]),
                }
            )
    return records


def similarity(left: str, right: str) -> tuple[float, float]:
    sequence = SequenceMatcher(None, left, right).ratio()
    left_tokens, right_tokens = set(left.split()), set(right.split())
    union = left_tokens | right_tokens
    jaccard = len(left_tokens & right_tokens) / len(union) if union else 1.0
    return sequence, jaccard


def leakage(rows: list[dict[str, Any]], prior: list[dict[str, str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for row in rows:
        normalized = plain(row["text"])
        best: dict[str, Any] | None = None
        for candidate in prior:
            sequence, jaccard = similarity(normalized, candidate["normalized"])
            is_risk = normalized == candidate["normalized"] or (sequence >= 0.92 and jaccard >= 0.80)
            if is_risk and (best is None or sequence > best["sequence_similarity"]):
                best = {
                    "external_id": row["id"],
                    "external_text": row["text"],
                    "external_normalized": normalized,
                    "prior_corpus": candidate["corpus"],
                    "prior_id": candidate["id"],
                    "prior_text": candidate["text"],
                    "sequence_similarity": round(sequence, 4),
                    "token_jaccard": round(jaccard, 4),
                    "match_type": "EXACT_SKELETON" if normalized == candidate["normalized"] else "NEAR_DUPLICATE",
                }
        if best:
            findings.append(best)
    return findings


def write_lines(path: Path, values: list[str]) -> None:
    path.write_text("".join(f"{value}\n" for value in values), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rows = load_jsonl(args.dataset)
    dev, heldout, keys = split(rows)
    findings = leakage(rows, prior_texts(args.root))
    excluded = sorted(item["external_id"] for item in findings)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_lines(args.output_dir / "external-dev-v1.ids.txt", dev)
    write_lines(args.output_dir / "external-heldout-v1.ids.txt", heldout)
    write_lines(args.output_dir / "external-leakage-risk-v1.ids.txt", excluded)

    split_report = {
        "dataset_version": "external-cuenca-v1",
        "algorithm": "phenomenon-stratified complete structural families; deterministic SHA-256 order",
        "seed": SEED,
        "records": len(rows),
        "dev_records": len(dev),
        "heldout_records": len(heldout),
        "families": len(set(keys.values())),
        "dev_ids": dev,
        "heldout_ids": heldout,
        "family_by_id": keys,
        "heldout_by_phenomenon": dict(
            sorted(Counter(row["phenomenon"] for row in rows if row["id"] in set(heldout)).items())
        ),
        "heldout_by_source": dict(
            sorted(Counter(row["source_id"] for row in rows if row["id"] in set(heldout)).items())
        ),
    }
    (args.output_dir / "external-split-v1.json").write_text(
        json.dumps(split_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    leakage_report = {
        "method": {
            "normalization": "lowercase, accents/punctuation removed, number words and digits -> <num>, placeholders -> <persona>",
            "risk_rule": "exact normalized skeleton OR SequenceMatcher >= 0.92 and token Jaccard >= 0.80",
        },
        "external_records": len(rows),
        "leakage_risk_records": len(findings),
        "findings": findings,
    }
    (args.output_dir / "external-leakage-v1.json").write_text(
        json.dumps(leakage_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "dev": len(dev),
        "heldout": len(heldout),
        "families": split_report["families"],
        "leakage_risk": len(findings),
    }, indent=2))


if __name__ == "__main__":
    main()
