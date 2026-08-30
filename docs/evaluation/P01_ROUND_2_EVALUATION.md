# Evaluación de P01 Round 2

**Evidencia:** `P01_R2 / REAL_DEVELOPMENT / Engine 1.1.0`

**Estado:** cerrado y congelado

| Métrica | Resultado | Límite |
|---|---:|---|
| Inputs | 27 | 24 no tienen outcome terminal. |
| Outcomes terminales | 3 confirmados | 0 corregidos, rechazados o cancelados. |
| Operaciones confirmadas | 3 | Venta, gasto y abono. |
| Context requests persistidos | 1 | Engine 1.1 no registraba este evento para toda propuesta incompleta. |
| `AMBIGUOUS` / `COMPOUND` / `OUT_OF_SCOPE` | 4 / 5 / 2 | Estados iniciales, no ground truth. |
| Respuestas iniciales sin operación | 12/27 | Manejo no final; corrección semántica independiente `NOT_MEASURABLE`. |
| Latencia de interpretación | mediana 0,272 ms; p95 2,1942 ms | No es tiempo total de UX. |
| Violaciones financieras críticas confirmadas | 0 observadas | Solo tres aceptaciones; no demuestra tasa poblacional. |

`CONFIRMED` significa `USER_ACCEPTED_OPERATION`, no ground truth perfecto. Exactitud de intención/campos, successful registration rate, correction/rejection/cancellation rate, tiempo a registrar, utilidad, recurrencia, confianza y preferencia por voz son `NOT_MEASURABLE` con estos outcomes incompletos.

## Gate de campo

`FIELD_CONTINUE`, no `FIELD_VALIDATED`. La ronda demuestra tres registros reales completados y revela defectos generalizables, pero un participante y tres outcomes no validan mercado ni precisión. P01 queda en development; P01_R3 solo puede empezar después del despliegue versionado y una nueva aceptación de consentimiento.
