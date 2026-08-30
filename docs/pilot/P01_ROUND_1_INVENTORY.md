# Inventario de P01 Round 1

**Corte administrativo:** 30 de agosto de 2026, 06:56:53 UTC  
**Participante:** `P01`  
**Ronda:** `P01_R1`  
**Rol:** `REAL_DEVELOPMENT`  
**Motor desplegado durante toda la captura:** `1.0.0`

## Alcance

Este inventario describe lo que existe, sin convertir aceptación, propuesta o ausencia de corrección en verdad de campo. P01 Round 1 fue una prueba real del canal de captura, pero no produjo operaciones confirmadas ni etiquetas humanas de corrección. No es `REAL_HELDOUT` y no valida mercado.

## Conteos congelados

| Elemento | Conteo |
|---|---:|
| Participantes pseudónimos | 1 |
| Sesiones | 2 |
| Sesiones cerradas administrativamente | 2 |
| Eventos | 71 |
| `TEXT_SUBMITTED` | 25 |
| `INTERPRETATION_CREATED` | 25 |
| `CONFIRMATION_SHOWN` | 14 |
| `CONTEXT_REQUESTED` | 3 |
| `SESSION_STARTED` / `SESSION_ENDED` | 2 / 2 |
| Operaciones persistidas | 0 |
| Cuentas por cobrar persistidas | 0 |
| Correcciones / confirmaciones / rechazos / cancelaciones | 0 / 0 / 0 / 0 |
| Feedback de sesión | 0 |
| Sesiones de acceso activas después del cierre | 0 |

Las sesiones fueron cerradas con `closure_type=ABANDONED_SESSION_CLOSED` y `closed_by=OPERATOR_TOOL`. El cierre es administrativo y no representa una acción del participante.

## Ventana temporal y versiones

- Primer evento: 30 de agosto de 2026, 05:46:38 UTC.
- Último evento de uso: 30 de agosto de 2026, 05:58:03 UTC.
- Cierre administrativo: 30 de agosto de 2026, 06:56:53 UTC.
- Ventana observable de actividad: aproximadamente 11 minutos y 26 segundos.
- Versiones observadas: `engine 1.0.0`, `rules-v0.1.0+explicit-v0.3.0+context-v0.2.0+safety-v0.1.0`, `operation-v0.1.0`, `pilot-v0`, `pilot-ui-v0`, `consent-v1`.

La duración hasta el cierre administrativo no debe reportarse como tiempo de uso.

## Distribución inicial

| Estado inicial | Conteo |
|---|---:|
| `NEEDS_CONFIRMATION` | 7 |
| `NEEDS_CONTEXT` | 7 |
| `COMPOUND_OPERATION` | 5 |
| `COMPLETE` | 3 |
| `AMBIGUOUS` | 2 |
| `OUT_OF_SCOPE` | 1 |

Se produjeron 14 propuestas de operación y 11 respuestas seguras sin operación. Sin outcomes terminales ni ground truth independiente no es posible afirmar cuántas propuestas fueron correctas.

## Custodia

El export privado reproducible permanece fuera de Git. Los hashes y metadatos auditables están en [`P01_ROUND_1_LOCK.md`](P01_ROUND_1_LOCK.md); la evaluación limitada está en [`P01_ROUND_1_EVALUATION.md`](../evaluation/P01_ROUND_1_EVALUATION.md).
