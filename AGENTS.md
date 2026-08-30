# MercadoVoz agent guide

## Mission and current gates

MercadoVoz converts natural-language business notes into safe, reviewable operations. Current state: `TECHNICAL_GO`, private pilot prepared, field validation pending. Never claim merchant validation, production readiness or real-user accuracy without new evidence.

## Repository boundaries

- `apps/web`: Next.js UI. It displays server contracts and never invents financial values.
- `apps/api`: FastAPI entry point and deployment boundary.
- `engine`: deterministic interpretation, workflow, persistence, schemas and migrations.
- `tests`: integration, regression and evaluation checks. E2E must use synthetic data.
- `research`: only synthetic or public/web-derived versionable evidence.
- `data`: runtime/private paths only; no real files in Git.
- `docs`: decisions and evidence. Preserve historical reports.

## Engine freeze

The files listed in `docs/pilot/PILOT_ENGINE_LOCK.md` are frozen for `pilot-v0`. Moving them is allowed only if their byte hashes remain identical. Do not change parser rules, normalization, safety, context resolution, extraction, classification or corrections during an active field round. Record errors; do not patch per phrase.

A later behavioral change requires:

1. close and hash the active dataset round;
2. classify a general error cause;
3. create a new engine version and lock;
4. rerun all regressions and separate benchmarks;
5. document safety and before/after evidence.

## Dataset classes

- `SYNTHETIC`: versionable test/evaluation cases.
- `WEB_DERIVED`: public evidence-derived exploratory corpus.
- `WEB_DERIVED_MULTISOURCE`: external Cuenca/Ecuador benchmark with provenance.
- `MANUAL_REGRESSION_DEVELOPMENT`: development-only phrases observed manually; never field or held-out evidence.
- `REAL_DEVELOPMENT`: private participant data used for iteration; never Git.
- `REAL_HELDOUT`: private, participant-separated evaluation; never Git.

Never combine these into one accuracy metric. Absence of real evidence is not evidence of zero errors.

## Privacy and security

Never commit databases, WAL files, exports, backups, participant mappings, audio, logs containing user text, credentials or `.env` files. Use aliases rather than identity. Consent is required before a real session. Do not print or copy configured secrets.

Before a public push, run both filesystem and staged scans for secrets, real data and large artifacts. Stop with `PUBLIC_REPO_BLOCKED` if anything sensitive remains.

## Commands

```powershell
python -m pip install -e ".[api]"
python -m unittest discover -s tests -v

Set-Location apps\web
npm ci
npm run typecheck
npm run build
npm audit --omit=dev
```

Evaluation outputs must go to ignored `data/runtime/` or another private path. Verify the baseline and engine hashes against their lock documents.

## Git policy

Permanent branches: `main`, `develop`. Work through `feature/*`, `fix/*`, `docs/*`, `chore/*`; use `release/*` only for a real release and `hotfix/*` only from `main`. Use Conventional Commits. Never force push, rewrite remote history, create a release/tag automatically or deploy from CI.

## Deployment boundary

The prepared target is Oracle Cloud Ampere A1 Flex with Ubuntu 24.04 ARM64, Nginx, PM2 for Next.js, systemd for FastAPI and SQLite WAL outside the repository. Deployment, DNS, credentials, P01 enrollment and opening public access require explicit authorization. Do not deploy as part of repository maintenance.

## Forbidden scope

No voice, LLM, inventory suite, SRI/e-invoicing, CRM, WhatsApp integration, multi-branch business roles or marketing launch unless a later evidence gate explicitly authorizes it.
