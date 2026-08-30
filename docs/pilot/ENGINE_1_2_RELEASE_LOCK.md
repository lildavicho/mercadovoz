# Lock de liberación — Engine 1.2.0

**Gate:** `ENGINE_1_2_RELEASE_CANDIDATE_GO`

**Versión:** `1.2.0`

**Commit de contenido validado:** `aefcb3f76deda7dada369c62a05bb9c8c7fbedb8` (`develop`, merge de PR #5).

**CI de contenido:** Python y Web `SUCCESS` en GitHub Actions run `33333800012`.

**Schema de operación:** `operation-v0.2.0`

**Migración persistente:** `004_batch_transaction_groups`

**Parser:** `rules-v0.1.0+explicit-v0.5.0+context-v0.2.0+safety-v0.2.0`

**Batch schema:** `batch-operation-v1`

**Pilot/UI:** `pilot-v0` / `pilot-ui-v0`

## Matriz bloqueada

- Python: 96 pruebas verdes.
- Web: 7 pruebas verdes; typecheck y build de producción verdes.
- P01_R1 replay 1.2: cero violaciones críticas; SHA-256 `98c7be160bb3539fbec71e24e1deec026b36a7490bc9e41cd479f57bb8ef99f0`.
- P01_R2 replay 1.2: 23 iguales, 4 mejoras, cero regresiones/violaciones críticas; SHA-256 `9f9765b71c3ad83d2ec6732bbfdd029410c3142f59da39607feab0dfa6ca1ada`.
- Corpus natural manual: SHA-256 `88d92064245bb8c7ef3b06cb634d34ee136a734e11ca99fa4431861584709ec6`.
- Batch web-derived: SHA-256 `985b85ae0f392165fe21f621c14f9a5dc5a7b6590123eb8a7316fe788961763b`.
- Batch sintético: SHA-256 `5cc0d4a2cc89a99a215499579112bd7b68a9320a98b49b64a541cef34cb64055`.
- Migración 004: SHA-256 `b0052e4568513c58e4736c6b21be9da365e01aff4508b5bbe3e5ffcedd1bdf55`.
- Upgrade sobre copia representativa 003→004: 4 sesiones, 148 eventos y 3 operaciones preservadas; R1/R2 legibles.
- npm audit de producción: cero vulnerabilidades conocidas.

## Límites de la liberación

El gate libera Engine 1.2 para el flujo individual. No emite validación de campo, `BATCH_GENERALIZATION_GO` ni `VOICE_FIELD_GO`. Batch y voz deben permanecer apagados en Oracle. Las limitaciones restantes producen abstención/revisión; no se observó un error financiero peligroso en los conjuntos evaluados.
