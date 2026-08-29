from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


CONTEXT_KEYS = {
    "active_product",
    "active_customer",
    "active_receivable",
    "active_stock_item",
    "pending_operation",
    "previous_operation",
    "session_context",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must include a timezone")


@dataclass(frozen=True)
class ContextValue:
    value: Any
    source: str
    observed_at: datetime
    expires_at: datetime
    invalidated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("context source is required")
        _require_aware(self.observed_at, "observed_at")
        _require_aware(self.expires_at, "expires_at")
        if self.expires_at <= self.observed_at:
            raise ValueError("expires_at must be later than observed_at")
        if self.invalidated_at is not None:
            _require_aware(self.invalidated_at, "invalidated_at")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    @property
    def created_at(self) -> datetime:
        return self.observed_at

    def is_available(self, now: datetime | None = None) -> bool:
        current = now or utc_now()
        _require_aware(current, "now")
        return self.invalidated_at is None and current < self.expires_at

    def snapshot(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "observed_at": self.observed_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "invalidated_at": self.invalidated_at.isoformat() if self.invalidated_at else None,
            "metadata": dict(self.metadata),
            "confidence": self.confidence,
        }


class ContextSession:
    """Explicit, expiring session context. It never guesses or persists values."""

    def __init__(self) -> None:
        self._values: dict[str, ContextValue] = {}

    def set(
        self,
        key: str,
        value: Any,
        *,
        source: str,
        observed_at: datetime | None = None,
        ttl: timedelta = timedelta(minutes=15),
        metadata: dict[str, Any] | None = None,
        confidence: float | None = None,
    ) -> ContextValue:
        if key not in CONTEXT_KEYS:
            raise KeyError(f"unsupported context key: {key}")
        if ttl <= timedelta(0):
            raise ValueError("ttl must be positive")
        observed = observed_at or utc_now()
        entry = ContextValue(
            value=value,
            source=source,
            observed_at=observed,
            expires_at=observed + ttl,
            metadata=metadata or {},
            confidence=confidence,
        )
        self._values[key] = entry
        return entry

    def get(self, key: str, *, now: datetime | None = None) -> ContextValue | None:
        if key not in CONTEXT_KEYS:
            raise KeyError(f"unsupported context key: {key}")
        entry = self._values.get(key)
        return entry if entry and entry.is_available(now) else None

    def invalidate(self, key: str, *, at: datetime | None = None) -> ContextValue | None:
        entry = self._values.get(key)
        if entry is None:
            return None
        invalidated = at or utc_now()
        _require_aware(invalidated, "invalidated_at")
        replacement = ContextValue(
            value=entry.value,
            source=entry.source,
            observed_at=entry.observed_at,
            expires_at=entry.expires_at,
            invalidated_at=invalidated,
            metadata=entry.metadata,
            confidence=entry.confidence,
        )
        self._values[key] = replacement
        return replacement

    def clear_expired(self, *, now: datetime | None = None) -> list[str]:
        current = now or utc_now()
        removed = [key for key, value in self._values.items() if not value.is_available(current)]
        for key in removed:
            del self._values[key]
        return removed

    def snapshot(self, *, now: datetime | None = None, include_unavailable: bool = False) -> dict[str, Any]:
        current = now or utc_now()
        return {
            key: value.snapshot()
            for key, value in self._values.items()
            if include_unavailable or value.is_available(current)
        }
