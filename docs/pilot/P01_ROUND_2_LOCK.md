# Lock de P01 Round 2

**Estado:** `P01_ROUND_2_STATUS = FROZEN`

**Dataset:** `P01_R2_REAL_DEVELOPMENT_v1`

**Motor:** `1.1.0`

**Parser:** `rules-v0.1.0+explicit-v0.4.0+context-v0.2.0+safety-v0.2.0`

**Schema:** `operation-v0.1.0`

**Commit desplegado:** `47dabdcf8eaca9ce71fdf164fc7893b691ba92c1`

## Cierre y alcance

Las dos sesiones `e9297d40-9431-4db1-a7a0-b7a9f21e3965` y `76f8ed6e-c90d-4ce6-8c0e-ccec7562d2f5` seguían abiertas. Se cerraron a `2026-08-30T19:49:43.289292+00:00` con `closure_type=ABANDONED_SESSION_CLOSED` y `closed_by=OPERATOR_TOOL`; dos accesos fueron revocados. No se atribuyó un cierre al participante.

## Backup pre-freeze

- `/home/ubuntu/backups/mercadovoz/p01-r2-pre-freeze-20260830T195000Z.db`
- SHA-256 `3007016d779699be402e07e8396c5f0c7f60daf4a888a15284888803c368b6f4`
- `PRAGMA integrity_check = ok`
- método `sqlite3.Connection.backup`; migraciones `001`, `002`, `003`.

## Export privado

Ruta: `/home/ubuntu/private_exports/mercadovoz/p01/r2/`; permisos privados y fuera de Git.

| Archivo | Registros | SHA-256 |
|---|---:|---|
| `p01-r2-real-development.jsonl` | 27 | `c528af5f48113a3627f3a2bf135f3142db4c754f30bc34cb9a5e7d5a6c53a16b` |
| `p01-r2-events.csv` | 77 | `20a473f19c916707f3ad52bb61dff252e9a8c1c589972358548a52c7bc7297db` |
| `p01-r2-operations.csv` | 3 | `6faa22bb7c6e59e460406494f1e67a1cfaa8e36e63e0c861785856666d011bb5` |
| `p01-r2-summary.json` | — | `3a8531639fd84b770668c3f9a57cbcea6d383b99eae94f964d5afe9fb6f7fc05` |
| `p01-r2-manifest.json` | — | `d10e490d8c62dde968437868e2c6dc84a078cc8a281c56bc5b090304a626d257` |

El export contiene 27 inputs, 77 eventos, 3 outcomes confirmados y 3 operaciones. Es `REAL_DEVELOPMENT`, nunca `REAL_HELDOUT`. Los replay 1.1/1.2 son artefactos derivados privados y no modifican esta evidencia. Cualquier corrección requiere una nueva versión y nuevos hashes; está prohibido regenerar o editar silenciosamente estos archivos.
