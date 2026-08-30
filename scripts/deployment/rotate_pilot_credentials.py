"""Rotate pilot credentials without emitting secret values."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROUND_PATTERN = re.compile(r"^P\d{2}_R\d+$")


def atomic_private_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()


def rotate(env_path: Path, operator_output: Path, *, origin: str, round_id: str) -> dict[str, str]:
    if not ROUND_PATTERN.fullmatch(round_id):
        raise ValueError("round_id must match PNN_RN")
    if not origin.startswith("https://") or origin.endswith("/"):
        raise ValueError("origin must be an HTTPS origin without trailing slash")

    existing = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    replacements = {
        "MERCADOVOZ_PILOT_ACCESS_CODES": json.dumps(
            {"P01": secrets.token_urlsafe(32)}, separators=(",", ":")
        ),
        "MERCADOVOZ_OPERATOR_TOKEN": secrets.token_urlsafe(48),
        "MERCADOVOZ_PILOT_ROUND_ID": round_id,
        "MERCADOVOZ_ALLOWED_ORIGINS": origin,
        "MERCADOVOZ_ENV": "pilot",
    }
    output: list[str] = []
    replaced: set[str] = set()
    for line in existing:
        key = line.split("=", 1)[0] if "=" in line else ""
        if key in replacements:
            output.append(f"{key}={replacements[key]}")
            replaced.add(key)
        else:
            output.append(line)
    for key, value in replacements.items():
        if key not in replaced:
            output.append(f"{key}={value}")
    atomic_private_write(env_path, "\n".join(output).rstrip() + "\n")

    created_at = datetime.now(timezone.utc).isoformat()
    access_code = json.loads(replacements["MERCADOVOZ_PILOT_ACCESS_CODES"])["P01"]
    operator_record = {
        "participant_id": "P01",
        "round_id": round_id,
        "access_code": access_code,
        "created_at": created_at,
        "retrieval": "sudo cat this file from the Oracle host; never paste it into Git or logs",
    }
    atomic_private_write(
        operator_output,
        json.dumps(operator_record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return {
        "env_path": str(env_path),
        "operator_output": str(operator_output),
        "round_id": round_id,
        "origin": origin,
        "rotated_at": created_at,
        "secret_values_printed": "false",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, type=Path)
    parser.add_argument("--operator-output", required=True, type=Path)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--round", required=True, dest="round_id")
    arguments = parser.parse_args()
    print(json.dumps(rotate(
        arguments.env,
        arguments.operator_output,
        origin=arguments.origin,
        round_id=arguments.round_id,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
