from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from mercadovoz.models import missing_fields, validate_operation

from .corrections import apply_controlled_correction


LIFECYCLE_STATUSES = {"PROPOSED", "CONFIRMED", "CORRECTED", "REJECTED", "CANCELLED"}
TERMINAL_STATUSES = {"CONFIRMED", "REJECTED", "CANCELLED"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OperationWorkflow:
    """In-memory confirmation workflow. It does not persist or execute operations."""

    def __init__(self) -> None:
        self._proposals: dict[str, dict[str, Any]] = {}
        self._idempotent_results: dict[tuple[str, str], dict[str, Any]] = {}

    def propose(self, interpretation: dict[str, Any]) -> dict[str, Any]:
        operation = interpretation.get("operation")
        if not operation:
            raise ValueError("an operation is required to create a proposal")
        proposal_id = str(uuid4())
        proposed_at = _now()
        record = {
            "proposal_id": proposal_id,
            "lifecycle_status": "PROPOSED",
            "interpretation_status": interpretation.get("status"),
            "original_text": interpretation.get("original_text"),
            "normalized_text": interpretation.get("normalized_text"),
            "parser_version": interpretation.get("parser_version"),
            "engine_version": interpretation.get("engine_version"),
            "schema_version": interpretation.get("schema_version"),
            "context_version": interpretation.get("context_version"),
            "context_used": deepcopy(interpretation.get("context_used", [])),
            "fields_extracted": deepcopy(interpretation.get("fields_extracted", {})),
            "computed_fields": deepcopy(interpretation.get("computed_fields", {})),
            "warnings": list(interpretation.get("warnings", [])),
            "missing_fields": list(interpretation.get("missing_fields", [])),
            "question": interpretation.get("question"),
            "safety_rules_triggered": list(interpretation.get("safety_rules_triggered", [])),
            "proposal": {"at": proposed_at, "operation": deepcopy(operation)},
            "confirmation": None,
            "corrections": [],
            "final_operation": None,
            "operation": deepcopy(operation),
            "audit_events": [{"at": proposed_at, "action": "PROPOSED"}],
        }
        self._proposals[proposal_id] = record
        return deepcopy(record)

    def get(self, proposal_id: str) -> dict[str, Any]:
        return deepcopy(self._require(proposal_id))

    def correct(self, proposal_id: str, correction_text: str) -> dict[str, Any]:
        record = self._require_mutable(proposal_id)
        result = apply_controlled_correction({"operation": record["operation"]}, correction_text)
        if "correction_not_understood" in result.get("warnings", []):
            record["audit_events"].append({"at": _now(), "action": "CORRECTION_NOT_UNDERSTOOD"})
            return deepcopy(record)
        record["operation"] = deepcopy(result["operation"])
        record["lifecycle_status"] = "CORRECTED"
        record["question"] = result.get("question")
        record["missing_fields"] = list(result.get("missing_fields", []))
        record["warnings"] = list(result.get("warnings", []))
        record["interpretation_status"] = result.get("status", "NEEDS_CONFIRMATION")
        correction = {
            "at": _now(),
            "text": correction_text,
            "warnings": list(result.get("warnings", [])),
        }
        record["corrections"].append(correction)
        record["audit_events"].append({"at": correction["at"], "action": "CORRECTED", "details": correction})
        return deepcopy(record)

    def confirm(self, proposal_id: str, *, idempotency_key: str) -> dict[str, Any]:
        if not idempotency_key.strip():
            raise ValueError("idempotency_key is required")
        cache_key = (proposal_id, idempotency_key)
        if cache_key in self._idempotent_results:
            return deepcopy(self._idempotent_results[cache_key])
        record = self._require(proposal_id)
        if record["lifecycle_status"] == "CONFIRMED":
            raise ValueError("proposal was already confirmed with another idempotency key")
        if record["lifecycle_status"] in {"REJECTED", "CANCELLED"}:
            raise ValueError("terminal proposal cannot be confirmed")
        operation = record["operation"]
        errors = [*missing_fields(operation), *validate_operation(operation)]
        if errors:
            raise ValueError(f"operation is not valid: {errors}")
        if record.get("interpretation_status") != "COMPLETE":
            raise ValueError(
                f"interpretation is not confirmable: {record.get('interpretation_status')}"
            )
        confirmed_at = _now()
        record["lifecycle_status"] = "CONFIRMED"
        record["confirmation"] = {"at": confirmed_at, "idempotency_key": idempotency_key}
        record["final_operation"] = deepcopy(operation)
        record["audit_events"].append({"at": confirmed_at, "action": "CONFIRMED"})
        result = deepcopy(record)
        self._idempotent_results[cache_key] = result
        return result

    def reject(self, proposal_id: str, *, reason: str) -> dict[str, Any]:
        return self._terminate(proposal_id, "REJECTED", reason)

    def cancel(self, proposal_id: str, *, reason: str) -> dict[str, Any]:
        return self._terminate(proposal_id, "CANCELLED", reason)

    def _terminate(self, proposal_id: str, status: str, reason: str) -> dict[str, Any]:
        record = self._require_mutable(proposal_id)
        record["lifecycle_status"] = status
        record["audit_events"].append({"at": _now(), "action": status, "details": {"reason": reason}})
        return deepcopy(record)

    def _require(self, proposal_id: str) -> dict[str, Any]:
        try:
            return self._proposals[proposal_id]
        except KeyError as exc:
            raise KeyError(f"unknown proposal: {proposal_id}") from exc

    def _require_mutable(self, proposal_id: str) -> dict[str, Any]:
        record = self._require(proposal_id)
        if record["lifecycle_status"] in TERMINAL_STATUSES:
            raise ValueError("terminal proposal cannot be changed")
        return record
