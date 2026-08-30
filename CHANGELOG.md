# Changelog

All notable repository-level changes are documented here. MercadoVoz has no public release yet.

## Unreleased

- Released Engine 1.2.0 to the private Oracle pilot under `P01_R3_READY_NOT_STARTED`; migration 004 preserved R1/R2 and the three historical operations.
- Kept Batch and Voice disabled after deployment; their independent gates remain on hold.

### Changed

- Froze `P01_R2` as 27 `REAL_DEVELOPMENT` records with three user-accepted operations, private exports and immutable hashes.
- Hardened Engine 1.2 customer extraction, explicit-total sales, uncertainty/self-correction safety and frontend/backend confirmability.
- Added a 100-narrative manually authored natural batch corpus and detailed boundary, crossover, partial recovery and source-span metrics.
- Added reproducible Engine 1.1/1.2 R2 replay and Engine 1.2 R1 replay without modifying historical evidence.

- Added experimental Engine 1.2 batch orchestration with exact source spans, item-level review and partial success behind disabled feature flags.
- Added atomic transaction groups, line items, receivable movements and explicit payment allocations through additive migration `004`.
- Added 3,000 synthetic batch cases, 60 web-derived compositions, 2,000 adversarial fuzz batches and separate reports.
- Added a provider-neutral voice transcription prototype with mandatory transcript review; it remains disabled and outside P01_R2.

- Bumped the candidate interpretation engine to `1.1.0` (`explicit-v0.4.0`, `safety-v0.2.0`).
- Added structured sale price/total boundaries, centavos handling and pronoun-safe payments.
- Strengthened compound, negation, plan/hypothesis and confirmation safety gates.
- Added generalized corrections, 3,600-case deterministic fuzz invariants and manual regression provenance.
- Added tested idempotency fallback and same-origin API support for temporary HTTP testing.
- Closed and froze `P01_R1`, deployed Engine 1.1 under explicit `P01_R2`, and added secure credential rotation tooling.
- Enabled HTTPS with automatic renewal and moved live secrets/exports outside the Git checkout.

### Safety

- Historical and external benchmarks remain separate; critical financial violations remain zero in the evaluated risk sets.
- Oracle currently remains on Engine `1.1.0`; R2 is closed/locked and 1.2 deployment is gated on release CI and predeploy backup.
- Closed P01 Round 1 administratively without inventing human outcomes, froze its private exports by hash and kept its Engine 1.0 evidence separate from the Engine 1.1 replay.
- Added explicit `round_id` persistence and reproducible round close, freeze and replay tooling for the P01 Round 2 boundary.

- Established the professional monorepo structure.
- Preserved and locked the deterministic interpretation engine.
- Added the Next.js private-pilot interface and FastAPI application boundary.
- Organized synthetic and public/web-derived research by provenance.
- Added private-pilot security, privacy, deployment and field documentation.
- Added continuous validation for Python and Next.js.

No version tag or release is associated with this entry.
