from __future__ import annotations

from typing import Any

from .context import ContextSession
from .engine import MercadoVozEngine
from .workflow import OperationWorkflow
from .storage import SQLiteLedger


class MercadoVozCore:
    """Stable in-process API; independent from CLI, HTTP and UI concerns."""

    def __init__(
        self,
        engine: MercadoVozEngine | None = None,
        storage: SQLiteLedger | None = None,
    ) -> None:
        self.engine = engine or MercadoVozEngine()
        self.workflow = OperationWorkflow()
        self.storage = storage

    def interpret(self, text: str, context: ContextSession | None = None) -> dict[str, Any]:
        return self.engine.interpret(text, context)

    def propose(self, text: str, context: ContextSession | None = None) -> dict[str, Any]:
        return self.workflow.propose(self.interpret(text, context))

    def correct(self, proposal_id: str, correction_text: str) -> dict[str, Any]:
        return self.workflow.correct(proposal_id, correction_text)

    def confirm(
        self,
        proposal_id: str,
        idempotency_key: str,
        *,
        participant_id: str | None = None,
        session_id: str | None = None,
        input_id: str | None = None,
    ) -> dict[str, Any]:
        record = self.workflow.confirm(proposal_id, idempotency_key=idempotency_key)
        if self.storage:
            record = {
                **record,
                "persisted_operation": self.storage.save_confirmed(
                    record,
                    participant_id=participant_id,
                    session_id=session_id,
                    input_id=input_id,
                ),
            }
        return record

    def reject(self, proposal_id: str, reason: str) -> dict[str, Any]:
        return self.workflow.reject(proposal_id, reason=reason)

    def cancel(self, proposal_id: str, reason: str) -> dict[str, Any]:
        return self.workflow.cancel(proposal_id, reason=reason)

    def history(self, limit: int = 50, participant_id: str | None = None) -> list[dict[str, Any]]:
        return self.storage.list_operations(limit, participant_id) if self.storage else []

    def receivables(self, participant_id: str | None = None) -> list[dict[str, Any]]:
        return self.storage.list_receivables(participant_id) if self.storage else []
