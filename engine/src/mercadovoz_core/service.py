from __future__ import annotations

import atexit
import hmac
import json
import logging
import os
import re
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mercadovoz_batch import BatchInterpreter, BatchLedger, BatchWorkflow

from .api import MercadoVozCore
from .context import ContextSession
from .pilot_version import CONSENT_VERSION, PILOT_VERSION, UI_VERSION
from .storage import SQLiteLedger
from .versioning import ENGINE_VERSION, PARSER_VERSION, SCHEMA_VERSION


logger = logging.getLogger("mercadovoz.pilot")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

PARTICIPANT_PATTERN = re.compile(r"^P\d{2}$")
ROUND_PATTERN = re.compile(r"^P\d{2}_R\d+$")


class ContextInput(BaseModel):
    value: Any
    source: str = "ui_visible_selection"
    ttl_seconds: int = Field(default=900, gt=0, le=3600)
    confidence: float | None = Field(default=None, ge=0, le=1)


class InterpretRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    context: dict[str, ContextInput] = Field(default_factory=dict)


class CorrectionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class ConfirmationRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=100)


class BatchInterpretRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    input_mode: str = Field(default="TEXT_BATCH", pattern=r"^(TEXT_SINGLE|TEXT_BATCH|VOICE_TRANSCRIPT)$")
    context: dict[str, ContextInput] = Field(default_factory=dict)


class BatchConfirmationRequest(BaseModel):
    item_ids: list[str] = Field(min_length=1, max_length=20)
    idempotency_key: str = Field(min_length=8, max_length=100)


class BatchCorrectionRequest(BaseModel):
    changes: dict[str, Any] = Field(min_length=1, max_length=10)


class ReasonRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=200)


class AccessRequest(BaseModel):
    participant_id: str = Field(pattern=r"^P\d{2}$")
    access_code: str = Field(min_length=8, max_length=200)


class ConsentRequest(BaseModel):
    consent_given: bool
    consent_version: str
    device_class: str = Field(default="unknown", pattern=r"^(mobile|tablet|desktop|unknown)$")


class FeedbackRequest(BaseModel):
    annoying: str = Field(default="", max_length=500)
    missing: str = Field(default="", max_length=500)
    distrust: str = Field(default="", max_length=500)
    faster: str = Field(default="", max_length=500)


def _context(values: dict[str, ContextInput]) -> ContextSession:
    session = ContextSession()
    for key, entry in values.items():
        session.set(
            key,
            entry.value,
            source=entry.source,
            ttl=timedelta(seconds=entry.ttl_seconds),
            confidence=entry.confidence,
        )
    return session


def _parse_access_codes(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("MERCADOVOZ_PILOT_ACCESS_CODES must be a JSON object") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("MERCADOVOZ_PILOT_ACCESS_CODES must be a JSON object")
    result = {str(key).upper(): str(value) for key, value in parsed.items()}
    if any(not PARTICIPANT_PATTERN.fullmatch(key) or len(value) < 8 for key, value in result.items()):
        raise RuntimeError("pilot access entries require PNN ids and codes of at least 8 characters")
    return result


def _versions(round_id: str) -> dict[str, str]:
    return {
        "engine_version": ENGINE_VERSION,
        "parser_version": PARSER_VERSION,
        "schema_version": SCHEMA_VERSION,
        "pilot_version": PILOT_VERSION,
        "ui_version": UI_VERSION,
        "round_id": round_id,
    }


def _operation_diff(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"field_changed": key, "old_value": before.get(key), "new_value": after.get(key)}
        for key in sorted(set(before) | set(after))
        if before.get(key) != after.get(key)
    ]


def create_app(
    database_path: str | Path | None = None,
    *,
    pilot_access_codes: dict[str, str] | None = None,
    pilot_mode: bool | None = None,
    operator_token: str | None = None,
    allowed_origins: list[str] | None = None,
    pilot_round_id: str | None = None,
    batch_experiment: bool | None = None,
) -> FastAPI:
    environment = os.environ.get("MERCADOVOZ_ENV", "development")
    is_pilot = pilot_mode if pilot_mode is not None else environment == "pilot"
    round_id = pilot_round_id or os.environ.get("MERCADOVOZ_PILOT_ROUND_ID", "")
    if not round_id and environment != "pilot":
        round_id = "SYNTHETIC_QA"
    if is_pilot and environment == "pilot" and not ROUND_PATTERN.fullmatch(round_id):
        raise RuntimeError("MERCADOVOZ_PILOT_ROUND_ID must match PNN_RN in pilot")
    db_path = database_path or os.environ.get("MERCADOVOZ_DB", "mercadovoz-mvp.db")
    storage = SQLiteLedger(db_path)
    core = MercadoVozCore(storage=storage)
    batch_enabled = batch_experiment if batch_experiment is not None else (
        os.environ.get("MERCADOVOZ_BATCH_EXPERIMENT", "false").lower() == "true"
    )
    batch_engine = BatchInterpreter()
    batch_workflow = BatchWorkflow()
    batch_storage = BatchLedger(storage)
    access_codes = pilot_access_codes if pilot_access_codes is not None else _parse_access_codes(
        os.environ.get("MERCADOVOZ_PILOT_ACCESS_CODES")
    )
    operator_secret = operator_token if operator_token is not None else os.environ.get("MERCADOVOZ_OPERATOR_TOKEN", "")
    origins = allowed_origins or [
        item.strip()
        for item in os.environ.get(
            "MERCADOVOZ_ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if item.strip()
    ]
    proposal_context: dict[str, dict[str, str]] = {}
    batch_context: dict[str, dict[str, str]] = {}
    access_attempts: dict[str, deque[float]] = defaultdict(deque)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        storage.close()

    app = FastAPI(
        title="MercadoVoz Pilot API",
        version=PILOT_VERSION,
        docs_url=None if is_pilot else "/docs",
        redoc_url=None,
        openapi_url=None if is_pilot else "/openapi.json",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Pilot-Session"],
    )

    @app.middleware("http")
    async def secure_and_log(request: Request, call_next):
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(json.dumps({"event": "server_error", "path": request.url.path}))
            raise
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        logger.info(json.dumps({
            "event": "http_request", "method": request.method,
            "path": request.url.path, "status": response.status_code,
            "duration_ms": elapsed,
        }, sort_keys=True))
        return response

    def guarded(action):
        try:
            return action()
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def bearer_token(authorization: str | None) -> str:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="pilot access required")
        return authorization.removeprefix("Bearer ").strip()

    def pilot_participant(authorization: Annotated[str | None, Header()] = None) -> str:
        token = bearer_token(authorization)
        participant_id = storage.participant_for_token(token)
        if participant_id is None:
            raise HTTPException(status_code=401, detail="pilot access expired or invalid")
        return participant_id

    def operator_access(authorization: Annotated[str | None, Header()] = None) -> None:
        token = bearer_token(authorization)
        if not operator_secret or not hmac.compare_digest(token, operator_secret):
            raise HTTPException(status_code=403, detail="operator access required")

    def active_session(
        participant_id: str,
        session_id: str | None,
    ) -> dict[str, Any]:
        if not session_id:
            raise HTTPException(status_code=400, detail="X-Pilot-Session is required")
        return guarded(lambda: storage.require_active_session(session_id, participant_id))

    def require_proposal(proposal_id: str, participant_id: str, session_id: str) -> dict[str, str]:
        context = proposal_context.get(proposal_id)
        if not context or context["participant_id"] != participant_id or context["session_id"] != session_id:
            raise HTTPException(status_code=404, detail="proposal not found in this pilot session")
        return context

    def require_batch(batch_id: str, participant_id: str, session_id: str) -> dict[str, str]:
        context = batch_context.get(batch_id)
        if not context or context["participant_id"] != participant_id or context["session_id"] != session_id:
            raise HTTPException(status_code=404, detail="batch not found in this pilot session")
        return context

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "database": "ok" if storage.health() else "unavailable"}

    @app.get("/pilot/config")
    def pilot_config() -> dict[str, Any]:
        return {
            **_versions(round_id),
            "consent_version": CONSENT_VERSION,
            "field_validation_status": "PENDING_REAL_DATA",
            "input_mode": "TEXT",
        }

    @app.post("/pilot/access")
    def pilot_access(request: AccessRequest, raw_request: Request):
        client_key = raw_request.client.host if raw_request.client else "unknown"
        now = time.monotonic()
        attempts = access_attempts[client_key]
        while attempts and attempts[0] < now - 300:
            attempts.popleft()
        if len(attempts) >= 10:
            raise HTTPException(status_code=429, detail="too many access attempts; try later")
        attempts.append(now)
        expected = access_codes.get(request.participant_id)
        if not expected or not hmac.compare_digest(request.access_code, expected):
            raise HTTPException(status_code=401, detail="invalid pilot access")
        token = storage.create_access_session(request.participant_id)
        return {"access_token": token, "participant_id": request.participant_id, "expires_in_hours": 12}

    @app.post("/pilot/consent")
    def consent(
        request: ConsentRequest,
        participant_id: str = Depends(pilot_participant),
    ):
        if not request.consent_given or request.consent_version != CONSENT_VERSION:
            raise HTTPException(status_code=400, detail="current explicit consent is required")
        return storage.begin_pilot_session(
            participant_id=participant_id,
            consent_version=request.consent_version,
            versions=_versions(round_id),
            device_class=request.device_class,
        )

    @app.post("/pilot/interpret")
    def pilot_interpret(
        request: InterpretRequest,
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        session = active_session(participant_id, x_pilot_session)
        input_id = str(uuid4())
        storage.record_event(
            event_type="TEXT_SUBMITTED", session_id=session["id"], participant_id=participant_id,
            engine_version=ENGINE_VERSION, input_id=input_id,
            payload={"original_text": request.text, "input_mode": "TEXT"},
        )
        started = time.perf_counter()
        try:
            interpretation = core.interpret(request.text, _context(request.context))
        except Exception:
            storage.record_event(
                event_type="ERROR_SHOWN", session_id=session["id"], participant_id=participant_id,
                engine_version=ENGINE_VERSION, input_id=input_id,
                payload={"error_class": "INTERPRETATION_FAILURE"},
            )
            raise
        latency_ms = round((time.perf_counter() - started) * 1000, 3)
        storage.record_event(
            event_type="INTERPRETATION_CREATED", session_id=session["id"], participant_id=participant_id,
            engine_version=ENGINE_VERSION, input_id=input_id, duration_ms=latency_ms,
            payload={
                "interpretation_state": interpretation["status"],
                "predicted_operation": interpretation.get("operation", {}).get("type") if interpretation.get("operation") else None,
                "operation": interpretation.get("operation"),
                "fields": interpretation.get("fields_extracted", {}),
                "missing_fields": interpretation.get("missing_fields", []),
                "context_requested": interpretation["status"] in {"NEEDS_CONTEXT", "NEEDS_CONFIRMATION"},
                "context_used": interpretation.get("context_used", []),
                "warnings": interpretation.get("warnings", []),
                "safety_rules_triggered": interpretation.get("safety_rules_triggered", []),
                "latency_ms": latency_ms,
            },
        )
        if interpretation["status"] in {"NEEDS_CONTEXT", "NEEDS_CONFIRMATION"} and not interpretation.get("operation"):
            storage.record_event(
                event_type="CONTEXT_REQUESTED", session_id=session["id"], participant_id=participant_id,
                engine_version=ENGINE_VERSION, input_id=input_id,
                payload={"missing_fields": interpretation.get("missing_fields", []), "question": interpretation.get("question")},
            )
        if not interpretation.get("operation"):
            return {**interpretation, "input_id": input_id}
        proposal = core.workflow.propose(interpretation)
        proposal_context[proposal["proposal_id"]] = {
            "participant_id": participant_id, "session_id": session["id"], "input_id": input_id,
        }
        storage.record_event(
            event_type="CONFIRMATION_SHOWN", session_id=session["id"], participant_id=participant_id,
            engine_version=ENGINE_VERSION, input_id=input_id,
            payload={"proposal_id": proposal["proposal_id"], "operation": proposal["operation"]},
        )
        return {**proposal, "input_id": input_id}

    if batch_enabled:
        @app.post("/pilot/interpret-batch")
        def pilot_interpret_batch(
            request: BatchInterpretRequest,
            participant_id: str = Depends(pilot_participant),
            x_pilot_session: Annotated[str | None, Header()] = None,
        ):
            session = active_session(participant_id, x_pilot_session)
            batch = batch_workflow.propose(batch_engine.interpret(
                request.text, _context(request.context), input_mode=request.input_mode,
            ))
            batch_storage.register(
                batch, participant_id=participant_id, session_id=session["id"],
            )
            batch_context[batch["batch_id"]] = {
                "participant_id": participant_id, "session_id": session["id"],
            }
            return batch

        @app.post("/pilot/batches/{batch_id}/items/{item_id}/correct")
        def pilot_correct_batch_item(
            batch_id: str,
            item_id: str,
            request: BatchCorrectionRequest,
            participant_id: str = Depends(pilot_participant),
            x_pilot_session: Annotated[str | None, Header()] = None,
        ):
            session = active_session(participant_id, x_pilot_session)
            require_batch(batch_id, participant_id, session["id"])
            item = guarded(lambda: batch_workflow.correct_item(batch_id, item_id, request.changes))
            guarded(lambda: batch_storage.update_item(batch_id, item, participant_id))
            return {"batch": batch_workflow.get(batch_id), "item": item}

        @app.post("/pilot/batches/{batch_id}/items/{item_id}/reject")
        def pilot_reject_batch_item(
            batch_id: str,
            item_id: str,
            request: ReasonRequest,
            participant_id: str = Depends(pilot_participant),
            x_pilot_session: Annotated[str | None, Header()] = None,
        ):
            session = active_session(participant_id, x_pilot_session)
            require_batch(batch_id, participant_id, session["id"])
            item = guarded(lambda: batch_workflow.terminate_item(batch_id, item_id, "REJECTED"))
            guarded(lambda: batch_storage.update_item(
                batch_id, item, participant_id, action="ITEM_REJECTED"
            ))
            return {"batch": batch_workflow.get(batch_id), "item": item, "reason": request.reason}

        @app.post("/pilot/batches/{batch_id}/items/{item_id}/cancel")
        def pilot_cancel_batch_item(
            batch_id: str,
            item_id: str,
            request: ReasonRequest,
            participant_id: str = Depends(pilot_participant),
            x_pilot_session: Annotated[str | None, Header()] = None,
        ):
            session = active_session(participant_id, x_pilot_session)
            require_batch(batch_id, participant_id, session["id"])
            item = guarded(lambda: batch_workflow.terminate_item(batch_id, item_id, "CANCELLED"))
            guarded(lambda: batch_storage.update_item(
                batch_id, item, participant_id, action="ITEM_REJECTED"
            ))
            return {"batch": batch_workflow.get(batch_id), "item": item, "reason": request.reason}

        @app.post("/pilot/batches/{batch_id}/confirm")
        def pilot_confirm_batch(
            batch_id: str,
            request: BatchConfirmationRequest,
            participant_id: str = Depends(pilot_participant),
            x_pilot_session: Annotated[str | None, Header()] = None,
        ):
            existing = guarded(lambda: batch_storage.result_for_key(
                participant_id, request.idempotency_key
            ))
            if existing is not None:
                return existing
            session = active_session(participant_id, x_pilot_session)
            require_batch(batch_id, participant_id, session["id"])
            batch = batch_workflow.get(batch_id)
            return guarded(lambda: batch_storage.confirm(
                batch,
                item_ids=request.item_ids,
                idempotency_key=request.idempotency_key,
                participant_id=participant_id,
                session_id=session["id"],
            ))

        @app.get("/pilot/transaction-groups")
        def pilot_transaction_groups(
            participant_id: str = Depends(pilot_participant),
            x_pilot_session: Annotated[str | None, Header()] = None,
        ):
            active_session(participant_id, x_pilot_session)
            return batch_storage.list_groups(participant_id)

    @app.post("/pilot/proposals/{proposal_id}/correct")
    def pilot_correct(
        proposal_id: str,
        request: CorrectionRequest,
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        session = active_session(participant_id, x_pilot_session)
        context = require_proposal(proposal_id, participant_id, session["id"])
        before = core.workflow.get(proposal_id)["operation"]
        corrected = guarded(lambda: core.correct(proposal_id, request.text))
        changes = _operation_diff(before, corrected["operation"])
        storage.record_event(
            event_type="OPERATION_CORRECTED", session_id=session["id"], participant_id=participant_id,
            engine_version=ENGINE_VERSION, input_id=context["input_id"],
            payload={
                "proposal_id": proposal_id, "changes": changes,
                "correction_method": "CONTROLLED_TEXT", "understood": bool(changes),
            },
        )
        return {**corrected, "input_id": context["input_id"]}

    @app.post("/pilot/proposals/{proposal_id}/confirm")
    def pilot_confirm(
        proposal_id: str,
        request: ConfirmationRequest,
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        session = active_session(participant_id, x_pilot_session)
        context = require_proposal(proposal_id, participant_id, session["id"])
        confirmed = guarded(lambda: core.confirm(
            proposal_id, request.idempotency_key,
            participant_id=participant_id, session_id=session["id"], input_id=context["input_id"],
        ))
        return {**confirmed, "input_id": context["input_id"]}

    def terminate_proposal(
        proposal_id: str, request: ReasonRequest, participant_id: str,
        session_id: str | None, outcome: str,
    ):
        session = active_session(participant_id, session_id)
        context = require_proposal(proposal_id, participant_id, session["id"])
        result = guarded(lambda: (
            core.reject(proposal_id, request.reason)
            if outcome == "OPERATION_REJECTED"
            else core.cancel(proposal_id, request.reason)
        ))
        storage.record_event(
            event_type=outcome, session_id=session["id"], participant_id=participant_id,
            engine_version=ENGINE_VERSION, input_id=context["input_id"],
            payload={"proposal_id": proposal_id, "reason_code": "USER_DECISION"},
        )
        return {**result, "input_id": context["input_id"]}

    @app.post("/pilot/proposals/{proposal_id}/reject")
    def pilot_reject(
        proposal_id: str, request: ReasonRequest,
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        return terminate_proposal(proposal_id, request, participant_id, x_pilot_session, "OPERATION_REJECTED")

    @app.post("/pilot/proposals/{proposal_id}/cancel")
    def pilot_cancel(
        proposal_id: str, request: ReasonRequest,
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        return terminate_proposal(proposal_id, request, participant_id, x_pilot_session, "OPERATION_CANCELLED")

    @app.get("/pilot/operations")
    def pilot_operations(
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
        limit: int = 50,
    ):
        active_session(participant_id, x_pilot_session)
        return core.history(min(max(limit, 1), 100), participant_id)

    @app.get("/pilot/receivables")
    def pilot_receivables(
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        active_session(participant_id, x_pilot_session)
        return core.receivables(participant_id)

    @app.get("/pilot/operations/{operation_id}/audit")
    def pilot_audit(
        operation_id: str,
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        active_session(participant_id, x_pilot_session)
        return guarded(lambda: storage.list_audit(operation_id, participant_id))

    @app.post("/pilot/feedback")
    def pilot_feedback(
        request: FeedbackRequest,
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        session = active_session(participant_id, x_pilot_session)
        return storage.save_feedback(session["id"], participant_id, request.model_dump())

    @app.post("/pilot/session/end")
    def pilot_session_end(
        participant_id: str = Depends(pilot_participant),
        x_pilot_session: Annotated[str | None, Header()] = None,
    ):
        session = active_session(participant_id, x_pilot_session)
        return storage.end_session(session["id"], participant_id, ENGINE_VERSION)

    @app.get("/pilot/operator/metrics", dependencies=[Depends(operator_access)])
    def operator_metrics(participant_id: str | None = None):
        return storage.metrics(participant_id)

    if not is_pilot:
        @app.post("/interpret")
        def interpret(request: InterpretRequest):
            return core.interpret(request.text, _context(request.context))

        @app.post("/proposals")
        def propose(request: InterpretRequest):
            return guarded(lambda: core.propose(request.text, _context(request.context)))

        @app.post("/proposals/{proposal_id}/correct")
        def correct(proposal_id: str, request: CorrectionRequest):
            return guarded(lambda: core.correct(proposal_id, request.text))

        @app.post("/proposals/{proposal_id}/confirm")
        def confirm(proposal_id: str, request: ConfirmationRequest):
            return guarded(lambda: core.confirm(proposal_id, request.idempotency_key))

        @app.post("/proposals/{proposal_id}/reject")
        def reject(proposal_id: str, request: ReasonRequest):
            return guarded(lambda: core.reject(proposal_id, request.reason))

        @app.post("/proposals/{proposal_id}/cancel")
        def cancel(proposal_id: str, request: ReasonRequest):
            return guarded(lambda: core.cancel(proposal_id, request.reason))

        @app.get("/operations")
        def operations(limit: int = 50):
            return core.history(min(max(limit, 1), 100))

        @app.get("/receivables")
        def receivables():
            return core.receivables()

    app.state.core = core
    app.state.storage = storage
    app.state.batch_engine = batch_engine
    app.state.batch_workflow = batch_workflow
    app.state.batch_storage = batch_storage
    app.state.batch_enabled = batch_enabled
    return app


app = create_app()
atexit.register(lambda: app.state.storage.close())


def main() -> None:
    import uvicorn

    host = "0.0.0.0" if os.environ.get("MERCADOVOZ_ENV") == "pilot" else "127.0.0.1"
    uvicorn.run("mercadovoz_core.service:app", host=host, port=int(os.environ.get("PORT", "8000")), reload=False)


if __name__ == "__main__":
    main()
