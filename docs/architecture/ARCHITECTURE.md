# Arquitectura — Core Engine v1 congelado y piloto privado

## Decisión

El parser v0 permanece inmutable como referencia histórica. La evolución vive en `mercadovoz_core`, una capa lateral y versionada que puede rechazarse sin reescribir resultados anteriores.

```text
texto original
    ↓
barrera de seguridad v0.1
    ├─ riesgo conocido → AMBIGUOUS / COMPOUND / OUT_OF_SCOPE / NEEDS_CONTEXT
    └─ sin bloqueo
           ↓
      parser de reglas v0.1 congelado
           ↓
      Context Layer v0.1 (solo valores explícitos y vigentes)
           ↓
      validación estructural y matemática
           ↓
      PROPOSED → CORRECTED → CONFIRMED
                 ├────────→ REJECTED
                 └────────→ CANCELLED
```

`COMPLETE` significa que la interpretación tiene los campos obligatorios; no significa guardada. Toda operación válida sigue en `PROPOSED` hasta una confirmación explícita e idempotente.

## Componentes implementados

```text
Browser
  ↓ HTTPS
Next.js (`apps/web`)
  ↓ JSON API
FastAPI (`apps/api` → `mercadovoz_core.service`)
  ↓
Interpretation Engine (`engine/src`)
  ├─ deterministic parser
  ├─ safety + explicit context
  ├─ PROPOSED / CORRECTED / REJECTED / CANCELLED
  └─ explicit confirmation gate
  ↓ confirmed transaction only
SQLite WAL
  ├─ operations + receivables
  ├─ participant/session boundaries
  └─ audit + evaluation events
```

La persistencia solo ocurre al confirmar. La `idempotency_key` impide duplicar una confirmación. La interfaz no calcula ni corrige totales por su cuenta: muestra el contrato devuelto por el core. Nginx es el único borde público previsto; Next.js y FastAPI escuchan únicamente en loopback en Oracle.

## Boundaries

- El navegador conserva un token efímero, pero no secretos de servidor ni autoridad sobre `participant_id`.
- FastAPI valida input, token, sesión, versiones y tenant antes de tocar persistencia.
- El engine no conoce hosting, Nginx ni identidad real; su contrato es determinista y versionado.
- SQLite almacena texto operativo controlado; logs técnicos no repiten texto financiero completo.
- `research/` y `docs/` no se copian al runtime de frontend ni API.

## Versiones

| Componente | Versión | Estado |
|---|---|---|
| parser determinista | `rules-v0.1.0` | congelado |
| seguridad previa | `safety-v0.1.0` | experimental |
| contexto | `context-v0.2.0` | experimental |
| schema | `operation-v0.1.0` | contrato vigente |
| core | `1.0.0` | gate técnico aprobado |
| parser compuesto | `explicit-rules-v1+rules-v0.1.0+context-v0.2.0+safety-v0.1.0` | usado en salida Sprint 1 |
| servicio | FastAPI local | Sprint 2 |
| persistencia | SQLite local | Sprint 2 |
| interfaz | Next.js/React/TypeScript/Tailwind | Sprint 2, solo texto |

## Context Layer v0

Solo admite estos campos:

| Campo | Ejemplo de fuente permitida | Caducidad sugerida | Invalidación |
|---|---|---:|---|
| `active_product` | selección visible del usuario | 15 min | cambio de producto/tarea |
| `active_customer` | selección visible del usuario | 15 min | cambio de cliente/tarea |
| `active_receivable` | cuenta seleccionada | 5 min | pago, cambio o cierre |
| `active_stock_item` | ítem seleccionado | 5 min | cambio o cierre |
| `pending_operation` | propuesta actual | sesión | confirmar/rechazar/cancelar |
| `previous_operation` | operación recién confirmada | 5 min | nueva tarea o cierre |
| `session_context` | configuración declarada | sesión | cierre o cambio explícito |

Cada valor exige `source`, `observed_at`, `expires_at` y admite `invalidated_at` y `metadata`. Los timestamps deben incluir zona horaria. Un valor vencido o invalidado no se usa. El snapshot de `context_used` conserva exactamente qué contexto influyó, con fuente y tiempos.

No se infiere contexto desde historial oculto, geolocalización, agenda, dispositivo ni similitud semántica. En v0.1 el contexto solo completa referencias controladas; no crea operaciones por sí mismo.

## Estados de interpretación

- `COMPLETE`: estructura completa y consistente; requiere confirmación.
- `NEEDS_CONFIRMATION`: hay operación parcial o corrección pendiente.
- `NEEDS_CONTEXT`: falta una selección explícita o la frase describe estado previo.
- `AMBIGUOUS`: dos lecturas con efecto material.
- `COMPOUND_OPERATION`: contiene más de una operación y debe dividirse.
- `OUT_OF_SCOPE`: intención sin schema aprobado.
- `UNSAFE`: reservado para una propuesta que viole un validador de seguridad.
- `UNRECOGNIZED`: no se reconoció una operación soportada.

Los estados de ciclo son independientes: `PROPOSED`, `CORRECTED`, `CONFIRMED`, `REJECTED` y `CANCELLED`.

## Contrato de auditoría

Cada interpretación/propuesta conserva:

- `original_text`, `normalized_text` y `parser_version`;
- `context_used`, `fields_extracted` y `computed_fields`;
- `warnings`, `confirmation`, `corrections` y `final_operation`;
- eventos con timestamp para propuesta, corrección y estado terminal.

La confirmación exige `idempotency_key`. Repetir la misma clave devuelve el mismo resultado; una clave distinta no puede confirmar por segunda vez. Esta implementación no guarda ni ejecuta operaciones y no sustituye una bitácora persistente transaccional.

## Límites

- Core: `SALE`, `EXPENSE`, `RECEIVABLE`, `PAYMENT_RECEIVED`.
- Exploratorio: `PURCHASE`, `STOCK_ADJUSTMENT`.
- Sin schema aprobado: retiro/aporte de propietario, cuentas por pagar y múltiples operaciones automáticas.
- Sin ASR, LLM, autenticación empresarial ni integración externa.
- SQLite opera en una sola instancia; el aislamiento P01–P08 existe, pero no es arquitectura SaaS multiempresa.
- Las propuestas viven en memoria; solo operaciones confirmadas y saldos persisten.
- Ningún componente prueba vocabulario, demanda o precisión de comerciantes reales.

## Criterios de aceptación del ciclo

1. 8/8 hashes del baseline v0 sin cambios.
2. Los cinco fallos P0 quedan como regresiones automatizadas.
3. Ninguna operación se confirma implícitamente.
4. Contexto vencido o invalidado no se usa y toda influencia queda auditada.
5. Cero propuestas de operación en los casos de operación esperada nula de P00/P01 exploratorios.
6. Corpus web y sintético siguen separados de evidencia real y del gate comercial.

## Capa `pilot-v0`

La interpretación anterior queda congelada por [`PILOT_ENGINE_LOCK.md`](../pilot/PILOT_ENGINE_LOCK.md). La capa nueva no cambia reglas; envuelve el motor con:

```text
protección proveedor + invitación
  → consentimiento versionado
  → sesión pseudónima
  → TEXT_SUBMITTED (original intacto)
  → motor congelado
  → INTERPRETATION_CREATED / CONFIRMATION_SHOWN
  → CORRECTED | REJECTED | CANCELLED | CONFIRMED
  → transacción SQLite: operación + audit event
  → métricas / export REAL_DEVELOPMENT
```

Tablas piloto separan participantes, consentimientos, access sessions, pilot sessions, eventos, feedback y anotaciones. `operations` y `receivables` llevan `participant_id` y `session_id`. La consulta exige que bearer token, participante y sesión coincidan.

## Versiones del piloto

| Componente | Versión |
|---|---|
| engine | `1.0.0` |
| parser | lock completo en `PILOT_ENGINE_LOCK.md` |
| pilot | `pilot-v0` |
| schema de operación | `operation-v0.1.0` |
| schema de eventos | `pilot-event-v1` |
| schema export | `real-development-v1` |
| UI | `pilot-ui-v0` |
| consentimiento | `consent-v1` |

## Trust boundaries

El cliente nunca decide participante, versión ni autorización. FastAPI deriva participante del token, valida sesión y añade versiones. El texto financiero vive en almacenamiento controlado y no en logs técnicos. El endpoint `/health` solo devuelve estado de app/DB. En `pilot`, documentación y rutas de laboratorio se desactivan.
