# Estado de MercadoVoz

**Actualizado:** 30 de agosto de 2026

| Campo | Estado |
|---|---|
| `TECHNICAL_STATUS` | `TECHNICAL_GENERALIZATION_GO` |
| `PARSER_STATUS` | `GENERALIZATION_REGRESSIONS_PASS` |
| `SAFETY_STATUS` | `CRITICAL_FINANCIAL_VIOLATIONS_0` |
| `CONTEXT_STATUS` | `TTL_AND_AUDIT_PASS` |
| `COMPOUND_STATUS` | `25/25 external; manual repeated-sale regression PASS` |
| `FIELD_VALIDATION_STATUS` | `PENDING_REAL_DATA` |
| `PILOT_STATUS` | `ACTIVE_DATA_PRESENT; ROUND_NOT_LOCKED` |
| `ENGINE_VERSION` | `1.1.0` (candidato; no desplegado) |
| `DEPLOYED_ENGINE_VERSION` | `1.0.0` |
| `PILOT_VERSION` | `pilot-v0` |
| `CURRENT_PARTICIPANTS` | `1` (`P01`, pseudónimo) |
| `REAL_DEVELOPMENT_RECORDS` | `25 inputs recolectados; no congelados ni versionados` |
| `REAL_HELDOUT_RECORDS` | `0` |
| `CRITICAL_ERRORS` | `0 en benchmarks; desconocido en datos reales aún no evaluados` |
| `LAST_GATE` | `LOCAL_GENERALIZATION_GATE_PASS` |
| `NEXT_GATE` | `HOLD_REAL_FIELD_DATA_REQUIRED: cerrar y congelar P01 Round 1 antes de cambiar el engine desplegado` |
| `DEPLOYMENT_STATUS` | `ORACLE_HTTP_TESTING; UPDATE_BLOCKED_ACTIVE_REAL_DATA` |

## Resultado técnico

- Las cinco regresiones manuales están separadas como `MANUAL_REGRESSION_DEVELOPMENT`.
- El parser histórico `rules-v0.1.0` y sus hashes no fueron reescritos.
- El candidato `engine 1.1.0` separa producto/precio, reconoce centavos, conserva totales declarados sin inventar precio unitario, excluye pronombres como clientes y detecta ventas repetidas/compuestas.
- Negaciones, planes, intenciones e hipótesis se abstienen; una interpretación no completa no puede confirmarse aunque su forma parezca válida.
- La matriz sintética generada ejecuta 3.600 combinaciones como prueba de robustez, no como evidencia de mercado.
- El benchmark externo conserva las métricas anteriores y cero violaciones financieras críticas. Véase [`GENERALIZATION_REPORT_2026-08-30.md`](../evaluation/GENERALIZATION_REPORT_2026-08-30.md).

## Estado de campo y despliegue

Oracle contiene dos sesiones abiertas de P01 bajo `engine 1.0.0`, 25 entradas y 69 eventos; no contiene operaciones confirmadas. Estos datos se tratan como reales y no se borran, editan ni mezclan con las regresiones manuales. El servidor permanece en HTTP temporal de prueba, por lo que no se declara listo para piloto de campo.

Se creó un backup consistente e íntegro fuera del repositorio antes de cualquier intento de actualización. No se realizó una restauración sobre la base activa.

Actualizar Oracle a `1.1.0` exige primero cerrar la ronda activa, exportarla mediante el mecanismo reproducible, registrar hashes y crear el lock de `REAL_DEVELOPMENT`. Hasta entonces el despliegue queda deliberadamente sin cambios.

## Gates

- `LLM_HOLD`: las reglas estructuradas todavía resuelven las clases observadas sin justificar un LLM.
- `VOICE_HOLD`: no existe evidencia humana suficiente de fricción al escribir.
- `FIELD_VALIDATION_STATUS = PENDING_REAL_DATA`: 25 inputs sin outcomes terminales no validan precisión, utilidad ni mercado.
- `HTTPS_REQUIRED`: HTTP solo sirve para pruebas controladas, no para recopilar nueva evidencia real.
