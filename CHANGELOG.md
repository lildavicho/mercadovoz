# Changelog

All notable repository-level changes are documented here. MercadoVoz has no public release yet.

## Unreleased

### Changed

- Bumped the candidate interpretation engine to `1.1.0` (`explicit-v0.4.0`, `safety-v0.2.0`).
- Added structured sale price/total boundaries, centavos handling and pronoun-safe payments.
- Strengthened compound, negation, plan/hypothesis and confirmation safety gates.
- Added generalized corrections, 3,600-case deterministic fuzz invariants and manual regression provenance.
- Added tested idempotency fallback and same-origin API support for temporary HTTP testing.

### Safety

- Historical and external benchmarks remain separate; critical financial violations remain zero in the evaluated risk sets.
- Oracle deployment remains on engine `1.0.0` until the active real-data round is closed and locked.
- Closed P01 Round 1 administratively without inventing human outcomes, froze its private exports by hash and kept its Engine 1.0 evidence separate from the Engine 1.1 replay.
- Added explicit `round_id` persistence and reproducible round close, freeze and replay tooling for the P01 Round 2 boundary.

- Established the professional monorepo structure.
- Preserved and locked the deterministic interpretation engine.
- Added the Next.js private-pilot interface and FastAPI application boundary.
- Organized synthetic and public/web-derived research by provenance.
- Added private-pilot security, privacy, deployment and field documentation.
- Added continuous validation for Python and Next.js.

No version tag or release is associated with this entry.
