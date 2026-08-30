# Inventario de P01 Round 2

**Corte:** 30 de agosto de 2026, 19:49:43 UTC

**Clasificación:** `P01_R2 / REAL_DEVELOPMENT / Engine 1.1.0`

**Cierre:** dos sesiones abandonadas cerradas por operador; no es `USER_CLOSED`

| Elemento | Conteo |
|---|---:|
| Sesiones / inputs / eventos | 2 / 27 / 77 |
| Interpretaciones / propuestas mostradas | 27 / 15 |
| Correcciones / confirmaciones / rechazos / cancelaciones | 0 / 3 / 0 / 0 |
| Solicitudes de contexto registradas | 1 |
| `AMBIGUOUS` / `OUT_OF_SCOPE` / `COMPOUND_OPERATION` | 4 / 2 / 5 |
| `NEEDS_CONTEXT` / `NEEDS_CONFIRMATION` / `COMPLETE` | 6 / 2 / 8 |
| Operaciones persistidas | 3: 1 venta, 1 gasto, 1 abono |
| Cuentas por cobrar creadas / abonos persistidos | 0 / 1 |
| `SESSION_STARTED` / `SESSION_ENDED` | 2 / 2 |

Los 15 eventos `CONFIRMATION_SHOWN` reflejan la implementación 1.1, que también mostraba propuesta para estados incompletos; no equivalen a 15 intentos terminales. Solo tres inputs tienen outcome humano terminal (`OPERATION_CONFIRMED`). Los 24 restantes no se reinterpretan como rechazo, cancelación o abandono de operación.

La primera sesión empezó a las 18:03:29 UTC, la última actividad observable ocurrió a las 19:39:29 UTC y el cierre administrativo fue a las 19:49:43 UTC. La diferencia hasta el cierre no es tiempo de uso.

Custodia y hashes: [`P01_ROUND_2_LOCK.md`](P01_ROUND_2_LOCK.md). Evaluación limitada: [`P01_ROUND_2_EVALUATION.md`](../evaluation/P01_ROUND_2_EVALUATION.md).
