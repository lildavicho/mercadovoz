# Estado de MercadoVoz

**Actualizado:** 30 de agosto de 2026

**URL privada:** `https://129-80-183-35.sslip.io`

| Campo | Estado |
|---|---|
| `TECHNICAL_STATUS` | `TECHNICAL_GENERALIZATION_GO` |
| `FIELD_VALIDATION_STATUS` | `PENDING_REAL_OUTCOMES` (25 inputs R1 congelados + 17 textos R2 provisionales; 0 outcomes terminales) |
| `PILOT_STATUS` | `P01_ROUND_2_ACTIVE` |
| `P01_ROUND_1_STATUS` | `FROZEN` |
| `P01_ROUND_1_ENGINE` | `1.0.0` |
| `P01_ROUND_2_STATUS` | `ACTIVE` |
| `HTTPS_STATUS` | `ACTIVE` |
| `ENGINE_VERSION` | `1.1.0` |
| `PARSER_VERSION` | `rules-v0.1.0+explicit-v0.4.0+context-v0.2.0+safety-v0.2.0` |
| `PILOT_VERSION` | `pilot-v0` |
| `SCHEMA_VERSION` | `operation-v0.1.0`; DB migration `003_pilot_round_id` |
| `UI_VERSION` | `pilot-ui-v0` |
| `ACTIVE_ROUND` | `P01_R2` |
| `CURRENT_PARTICIPANTS` | `1` (`P01`); `1` sesión abierta en R2 |
| `REAL_DEVELOPMENT_RECORDS` | `25`, congelados en `P01_R1` |
| `REAL_HELDOUT_RECORDS` | `0` |
| `CRITICAL_ERRORS` | `0` en benchmarks/replay; error humano R1 `NOT_MEASURABLE` |
| `LAST_GATE` | `HTTPS_AND_ROUND_ISOLATION_PASS` |
| `NEXT_GATE` | `P01_R2_FIRST_TERMINAL_OUTCOME_THEN_CLOSE_AND_FREEZE` |
| `DEPLOYMENT_STATUS` | `HTTPS_LIVE_PRIVATE_ACCESS` |
| `VOICE_STATUS` | `HOLD` |
| `LLM_STATUS` | `HOLD` |
| `BATCH_BRANCH_STATUS` | `BATCH_ENGINE_TECHNICAL_GO / BATCH_GENERALIZATION_HOLD` (no desplegado) |
| `BATCH_CANDIDATE_VERSION` | `1.2.0`, sidecar sobre Engine `1.1.0` |
| `VOICE_PROTOTYPE_STATUS` | `HOLD_PENDING_HARDWARE_PROVIDER_TEST`; código detrás de bandera apagada |

## Evidencia congelada

P01 Round 1 permanece como `P01_R1 / REAL_DEVELOPMENT / engine 1.0.0`: 2 sesiones cerradas administrativamente, 25 inputs, 71 eventos, 0 operaciones confirmadas y 0 outcomes terminales. Sus exports y hashes están en [`P01_ROUND_1_LOCK.md`](P01_ROUND_1_LOCK.md). El replay separado con Engine 1.1 produjo cero violaciones financieras críticas, pero no es ground truth ni R2.

## Ronda activa

Oracle ejecuta el commit de código `47dabdcf8eaca9ce71fdf164fc7893b691ba92c1`. `/pilot/config` confirma Engine `1.1.0`, `P01_R2`, consentimiento `pilot-consent-v1` y texto como único input. La auditoría agregada del 30 de agosto observa 1 sesión R2 abierta, 17 `TEXT_SUBMITTED`, 17 interpretaciones, 9 confirmaciones mostradas y 0 operaciones confirmadas. No se inspeccionó texto ni se ejecutó replay sobre R2.

El acceso P01 y el token de operador fueron rotados, permanecen root-only fuera de Git y los nueve tokens anteriores están revocados. El consentimiento no cambia porque finalidad, datos, retención y derechos no cambiaron.

## Gates

- `FIELD_ITERATE`: abrir R2 para obtener outcomes terminales y correcciones reales.
- `VOICE_HOLD`: no existe evidencia de que escribir sea la fricción decisiva.
- `LLM_HOLD`: no existe una clase de error real que justifique esa complejidad.
- `HTTPS_AND_ROUND_ISOLATION_PASS`: certificado válido, renovación simulada, redirección y `round_id` verificados.
- No decir “validado con comerciantes”, “market validated” ni accuracy real.
- La rama batch no cambia `ACTIVE_ROUND`, `NEXT_GATE`, versiones de Oracle ni evidencia P01. Su siguiente gate es una prueba batch natural separada después de cerrar y congelar R2.
