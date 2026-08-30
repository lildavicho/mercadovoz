# Replay congelado P01_R2 — Engine 1.1 vs 1.2

El mismo export de 27 inputs se ejecutó offline, sin escribir en Oracle ni en el dataset.

| Replay | Resultado | SHA-256 privado |
|---|---|---|
| Engine 1.1 | 27 `same`, 0 violaciones críticas | `f50a078a44134994a73fa50be1d7cb6bddc688aa9189aae38c1c166ad3e46212` |
| Engine 1.2 final | 23 `same`, 4 `improved`, 0 regresiones, 0 violaciones críticas | `9f9765b71c3ad83d2ec6732bbfdd029410c3142f59da39607feab0dfa6ca1ada` |

Las cuatro mejoras son las dos apariciones de la deuda con cliente explícito y las dos apariciones de la venta con total explícito. Las tres operaciones aceptadas por el usuario permanecen iguales. Los cambios sin ground truth no se convierten en accuracy.

**Gate:** `ENGINE_1_2_REPLAY_GO`.
