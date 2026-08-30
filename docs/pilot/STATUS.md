# Estado de MercadoVoz

**Actualizado:** 30 de agosto de 2026

**URL privada:** `https://129-80-183-35.sslip.io`

| Campo | Estado |
|---|---|
| `TECHNICAL_STATUS` | `TECHNICAL_GENERALIZATION_GO` |
| `FIELD_VALIDATION_STATUS` | `FIELD_CONTINUE` (52 inputs R1+R2; 3 outcomes terminales; no validación de mercado) |
| `PILOT_STATUS` | `P01_R2_FROZEN / P01_R3_READY_NOT_STARTED` |
| `P01_ROUND_1_STATUS` | `FROZEN` |
| `P01_ROUND_1_ENGINE` | `1.0.0` |
| `P01_ROUND_2_STATUS` | `FROZEN` |
| `HTTPS_STATUS` | `ACTIVE` |
| `ENGINE_VERSION` | Oracle `1.2.0` |
| `PARSER_VERSION` | `rules-v0.1.0+explicit-v0.5.0+context-v0.2.0+safety-v0.2.0` |
| `PILOT_VERSION` | `pilot-v0` |
| `SCHEMA_VERSION` | Oracle `operation-v0.2.0`; migraciones `001`–`004` |
| `UI_VERSION` | `pilot-ui-v0` |
| `ACTIVE_ROUND` | ninguna; `P01_R3` no iniciada |
| `CURRENT_PARTICIPANTS` | `0`; sesiones R2 cerradas y accesos revocados |
| `REAL_DEVELOPMENT_RECORDS` | `52`: R1 25 + R2 27, congelados por separado |
| `REAL_HELDOUT_RECORDS` | `0` |
| `CRITICAL_ERRORS` | `0` en R1/R2 replay, corpus natural, web-derived y sintético |
| `LAST_GATE` | `ENGINE_1_2_RELEASE_CANDIDATE_GO / P01_R3_READY` |
| `NEXT_GATE` | `P01_R3_MINIMUM_TERMINAL_OUTCOMES_AND_CLOSE` |
| `DEPLOYMENT_STATUS` | `ENGINE_1_2_HTTPS_LIVE_PRIVATE_ACCESS` |
| `VOICE_STATUS` | `HOLD` |
| `LLM_STATUS` | `HOLD` |
| `BATCH_BRANCH_STATUS` | `BATCH_ENGINE_TECHNICAL_GO / BATCH_NATURAL_DEVELOPMENT_EVALUATED / BATCH_GENERALIZATION_HOLD` |
| `BATCH_CANDIDATE_VERSION` | `1.2.0`, bandera de producción apagada |
| `VOICE_PROTOTYPE_STATUS` | `HOLD_PENDING_HARDWARE_PROVIDER_TEST`; código detrás de bandera apagada |

## Evidencia congelada

P01 Round 1 permanece como `P01_R1 / REAL_DEVELOPMENT / engine 1.0.0`: 2 sesiones cerradas administrativamente, 25 inputs, 71 eventos, 0 operaciones confirmadas y 0 outcomes terminales. Sus exports y hashes están en [`P01_ROUND_1_LOCK.md`](P01_ROUND_1_LOCK.md). El replay separado con Engine 1.1 produjo cero violaciones financieras críticas, pero no es ground truth ni R2.

## Ronda cerrada

Oracle ejecuta el release commit `2f5a570df11d3ae41e8cfc55208d28717b8cc739`, Engine 1.2.0 y migration 004. R2 fue cerrada administrativamente, respaldada, exportada y congelada: 2 sesiones, 27 inputs, 77 eventos y 3 operaciones confirmadas. El replay offline 1.2 preservó los tres outcomes, mejoró cuatro casos conocidos y tuvo cero regresiones/violaciones críticas.

El acceso P01 y el token de operador fueron rotados para R3, permanecen root-only fuera de Git y todos los tokens anteriores están revocados. El consentimiento no cambia porque finalidad, datos, retención y derechos no cambiaron. R3 no tiene sesiones ni inputs: solo está preparada.

## Gates

- `FIELD_CONTINUE`: preparar R3; tres outcomes no constituyen validación.
- `VOICE_HOLD`: no existe evidencia de que escribir sea la fricción decisiva.
- `LLM_HOLD`: no existe una clase de error real que justifique esa complejidad.
- `HTTPS_AND_ROUND_ISOLATION_PASS`: certificado válido, renovación simulada, redirección y `round_id` verificados.
- No decir “validado con comerciantes”, “market validated” ni accuracy real.
- Batch y voz permanecen OFF. El corpus batch natural manual pasó invariantes P0, pero la generalización externa/real sigue en hold.
