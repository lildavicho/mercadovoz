# Repository structure

```text
mercadovoz/
├── apps/
│   ├── api/                  # FastAPI entry point and deploy configuration
│   └── web/                  # Next.js mobile-first private pilot
├── engine/
│   ├── migrations/           # versioned SQLite schema changes
│   ├── schemas/              # operation contract
│   └── src/                  # frozen baseline and MercadoVozCore
├── tests/
│   ├── integration/          # API, storage, pilot and transaction boundaries
│   ├── regression/           # parser, safety, context and workflow
│   ├── evaluation/           # reproducibility checks
│   └── e2e/                  # critical browser protocol
├── research/
│   ├── benchmarks/           # synthetic/web-derived inputs and reports
│   ├── external-cuenca-v1/   # multisource corpus + manifests
│   └── SOURCE_LEDGER.md
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── deployment/
│   ├── evaluation/
│   ├── pilot/
│   └── product/
├── scripts/
│   ├── backup/
│   ├── deployment/
│   ├── evaluation/
│   ├── export/
│   └── pilot/
├── data/                     # README only; runtime/private files ignored
└── .github/                  # CI and contribution templates
```

There is no task runner or JavaScript workspace layer. Python packaging is managed from the root `pyproject.toml`; the web app owns its own `package.json`. Research never ships in either runtime build.
