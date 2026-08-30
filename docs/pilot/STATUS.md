# Estado de MercadoVoz

**Actualizado:** 30 de agosto de 2026

**URL privada:** `https://129-80-183-35.sslip.io`

| Campo | Estado |
|---|---|
| `TECHNICAL_STATUS` | `TECHNICAL_GENERALIZATION_GO` |
| `FIELD_VALIDATION_STATUS` | `PENDING_REAL_DATA` (25 inputs existen; outcomes humanos aún no medibles) |
| `PILOT_STATUS` | `P01_ROUND_2_READY` |
| `P01_ROUND_1_STATUS` | `FROZEN` |
| `P01_ROUND_1_ENGINE` | `1.0.0` |
| `P01_ROUND_2_STATUS` | `READY` |
| `HTTPS_STATUS` | `ACTIVE` |
| `ENGINE_VERSION` | `1.1.0` |
| `PARSER_VERSION` | `rules-v0.1.0+explicit-v0.4.0+context-v0.2.0+safety-v0.2.0` |
| `PILOT_VERSION` | `pilot-v0` |
| `SCHEMA_VERSION` | `operation-v0.1.0`; DB migration `003_pilot_round_id` |
| `UI_VERSION` | `pilot-ui-v0` |
| `ACTIVE_ROUND` | `P01_R2` |
| `CURRENT_PARTICIPANTS` | `1` histórico (`P01`); `0` sesiones abiertas en R2 |
| `REAL_DEVELOPMENT_RECORDS` | `25`, congelados en `P01_R1` |
| `REAL_HELDOUT_RECORDS` | `0` |
| `CRITICAL_ERRORS` | `0` en benchmarks/replay; error humano R1 `NOT_MEASURABLE` |
| `LAST_GATE` | `HTTPS_AND_ROUND_ISOLATION_PASS` |
| `NEXT_GATE` | `P01_R2_FIRST_CONSENT_AND_VALID_OPERATION` |
| `DEPLOYMENT_STATUS` | `HTTPS_LIVE_PRIVATE_ACCESS` |
| `VOICE_STATUS` | `HOLD` |
| `LLM_STATUS` | `HOLD` |

## Evidencia congelada

P01 Round 1 permanece como `P01_R1 / REAL_DEVELOPMENT / engine 1.0.0`: 2 sesiones cerradas administrativamente, 25 inputs, 71 eventos, 0 operaciones confirmadas y 0 outcomes terminales. Sus exports y hashes están en [`P01_ROUND_1_LOCK.md`](P01_ROUND_1_LOCK.md). El replay separado con Engine 1.1 produjo cero violaciones financieras críticas, pero no es ground truth ni R2.

## Ronda activa

Oracle ejecuta el commit de código `519ba141c15123023f24afed3efe0ae31dabab02`. `/pilot/config` confirma Engine `1.1.0`, `P01_R2`, consentimiento `pilot-consent-v1` y texto como único input. La base conserva solo R1 hasta que P01 acepte consentimiento y use R2; no se creó una sesión sintética en producción.

El acceso P01 y el token de operador fueron rotados, permanecen root-only fuera de Git y los nueve tokens anteriores están revocados. El consentimiento no cambia porque finalidad, datos, retención y derechos no cambiaron.

## Gates

- `FIELD_ITERATE`: abrir R2 para obtener outcomes terminales y correcciones reales.
- `VOICE_HOLD`: no existe evidencia de que escribir sea la fricción decisiva.
- `LLM_HOLD`: no existe una clase de error real que justifique esa complejidad.
- `HTTPS_AND_ROUND_ISOLATION_PASS`: certificado válido, renovación simulada, redirección y `round_id` verificados.
- No decir “validado con comerciantes”, “market validated” ni accuracy real.
