# Contributing

MercadoVoz uses a small branch model:

```text
feature/* → develop → release/* → main
fix/*     → develop
main → hotfix/* → main + develop
```

Only `main` and `develop` are permanent. Create `docs/*` for documentation-only work and `chore/*` for CI, dependencies or repository maintenance. Do not create empty future branches.

## Commits

Use Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:` or `ci:`. Keep commits focused and explain safety/data effects in the pull request.

## Validation

From the repository root:

```powershell
python -m pip install -e ".[api]"
python -m unittest discover -s tests -v
python scripts\evaluation\evaluate_engine.py research\benchmarks\synthetic\evaluation.jsonl heldout --output data\runtime\evaluation.json

Set-Location apps\web
npm ci
npm run typecheck
npm run build
```

Run the hash check documented in `docs/pilot/PILOT_ENGINE_LOCK.md` whenever engine files move or change.

## Pull requests

- Prefer PRs into `develop`; promote stable work through a release branch into `main`.
- Never modify the frozen engine during an active field round.
- Never use real participant data in tests, screenshots or fixtures.
- A behavioral engine change requires a new version, lock, benchmark and explicit safety review.
- Deployment remains manual until a later decision authorizes automation.

## Hotfixes

Branch from `main`, apply the smallest correction, validate, merge to `main`, then merge the same fix into `develop`. Do not force push protected history.
