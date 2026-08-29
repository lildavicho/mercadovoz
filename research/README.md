# Research data

Only evidence that is public, synthetic and safe to redistribute within this repository is versioned here.

| Class | Meaning | Git policy |
|---|---|---|
| `SYNTHETIC` | authored test/evaluation examples | versioned |
| `WEB_DERIVED` | exploratory records derived from public evidence | versioned with provenance |
| `WEB_DERIVED_MULTISOURCE` | Cuenca/Ecuador external benchmark from multiple public sources | versioned with source ledger and locks |
| `REAL_DEVELOPMENT` | consented participant data that may influence later iterations | never versioned |
| `REAL_HELDOUT` | consented, participant-separated field evaluation | never versioned |

`benchmarks/synthetic/` contains the historical development and held-out fixtures. `benchmarks/web-derived/` contains P00/P01-WEB exploratory corpora. `external-cuenca-v1/` preserves the supplied public-evidence corpus, manifests and source documentation without transformation. Historical machine-readable reports live in `benchmarks/results/`.

The provenance and restrictions are documented in [SOURCE_LEDGER.md](SOURCE_LEDGER.md), [LICENSE_AND_PROVENANCE.md](LICENSE_AND_PROVENANCE.md), the dataset locks under `docs/evaluation/`, and the external corpus README. A source appearing in the ledger is not automatically evidence for every record.

Never report one combined “accuracy” across classes. Public/web-derived evidence does not substitute for merchant validation.
