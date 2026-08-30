# Evaluación de P01 Round 1

**Dataset:** `P01_R1` / `REAL_DEVELOPMENT`  
**Motor observado:** `1.0.0`  
**Estado:** cerrado y congelado; evidencia humana incompleta

## Resultado medible

| Métrica | Resultado | Interpretación |
|---|---:|---|
| `TOTAL_INPUTS` | 25 | Envíos no vacíos preservados por eventos. |
| `PROPOSAL_RATE` | 14/25 (56%) | Propuesta estructurada; no implica corrección. |
| `CONTEXT_REQUEST_RATE` | 3/25 (12%) | Solicitudes explícitas registradas. |
| Respuestas seguras sin operación | 11/25 (44%) | Estados no finales; no equivalen automáticamente a abstenciones correctas. |
| Latencia de interpretación, mediana | 0,296 ms | Medición del motor almacenada; no es tiempo total de UX. |
| Latencia de interpretación, p95 | 4,1704 ms | Medición del motor almacenada. |
| Operaciones confirmadas | 0 | No existe `USER_ACCEPTED_OPERATION`. |
| Errores financieros críticos confirmados | 0 observados | No hubo operaciones confirmadas; no demuestra precisión financiera. |

## Métricas no calculables

`SUCCESSFUL_REGISTRATION_RATE`, `CONFIRMATION_RATE`, `CORRECTION_RATE`, `REJECTION_RATE`, `CANCELLATION_RATE`, `TIME_TO_REGISTER`, tiempo de confirmación, exactitud de intención/campos y utilidad de producto son `NOT_MEASURABLE` en esta ronda. Mostrar 14 tarjetas de confirmación no constituye 14 intentos terminales.

Tampoco pueden inferirse recurrencia, confianza, ahorro de tiempo, recuperación de deudas ni preferencia por voz. No hubo entrevista real asociada a este export.

## Lectura responsable

La ronda demuestra que el canal privado capturó 25 textos originales con versiones y trazabilidad, y que el motor evitó guardar operaciones silenciosamente. La ausencia total de outcomes terminales revela una brecha de observación/flujo: no permite saber si el participante abandonó por fricción, terminó fuera del registro, no comprendió el flujo o simplemente estaba probando.

El replay técnico con Engine 1.1 se reporta por separado en [`P01_R1_REPLAY_ENGINE_1_1.md`](P01_R1_REPLAY_ENGINE_1_1.md). Sus clasificaciones no son ground truth ni nueva evidencia de P01.

## Gate

**Decisión:** `FIELD_ITERATE`.

Se permite abrir `P01_R2` con motor versionado, HTTPS, credencial rotada, `round_id` persistido y el mismo consentimiento porque no cambia el tratamiento de datos. Se mantiene `FIELD_VALIDATION_STATUS=PENDING_REAL_DATA`, `VOICE_HOLD` y `LLM_HOLD`.
