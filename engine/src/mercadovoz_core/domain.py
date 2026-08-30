from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class Business:
    id: str
    name: str


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    default_unit: str | None = None


@dataclass(frozen=True)
class CustomerReference:
    id: str
    label: str


@dataclass(frozen=True)
class Operation:
    type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Sale(Operation):
    product: str
    quantity: int | float
    unit: str
    unit_price: int | float | None
    total: int | float
    type: Literal["SALE"] = field(default="SALE", init=False)


@dataclass(frozen=True)
class Expense(Operation):
    category: str
    amount: int | float
    type: Literal["EXPENSE"] = field(default="EXPENSE", init=False)


@dataclass(frozen=True)
class Receivable(Operation):
    customer: str
    amount: int | float
    type: Literal["RECEIVABLE"] = field(default="RECEIVABLE", init=False)


@dataclass(frozen=True)
class PaymentReceived(Operation):
    customer: str
    amount: int | float
    type: Literal["PAYMENT_RECEIVED"] = field(default="PAYMENT_RECEIVED", init=False)


@dataclass(frozen=True)
class AuditEvent:
    at: str
    action: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Confirmation:
    at: str
    idempotency_key: str


@dataclass(frozen=True)
class Correction:
    at: str
    text: str
    changed_fields: tuple[str, ...]


@dataclass
class PendingOperation:
    proposal_id: str
    operation: dict[str, Any]
    lifecycle_status: str = "PROPOSED"
    audit_events: list[AuditEvent] = field(default_factory=list)
