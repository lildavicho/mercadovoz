# ADR-002 — Explicit context layer

**Status:** accepted and frozen in engine 1.0.0.

## Context

Short merchant phrases can depend on a selected product, customer or receivable. Inferring those references from hidden history or similarity could create the wrong financial operation.

## Decision

Context is explicit, typed, source-attributed and expiring. Only supported keys may influence interpretation. Used context is recorded with timestamps; expired or invalidated values are ignored. Missing material context produces a request or abstention, never an invented value.

## Consequences

The workflow may require an extra turn, but interpretation is reproducible and auditable. Location, contacts, device fingerprint and semantic guesses are not context sources.
