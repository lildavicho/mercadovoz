# ADR-003 — Human confirmation before persistence

**Status:** accepted.

## Context

A technically plausible interpretation can still contain a financially material error. Silent persistence would turn parser uncertainty into business state.

## Decision

Every operation remains `PROPOSED` or `CORRECTED` until a person explicitly confirms it. The confirmation card exposes operation type and material fields. The person can correct, reject or cancel. Confirmation is idempotent; operation and audit event commit in one transaction.

## Consequences

`CONFIRMED` means `USER_ACCEPTED_OPERATION`, not perfect ground truth. The extra action is intentional safety friction and is measured during the pilot.
