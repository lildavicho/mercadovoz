# Lock de inicio — P01 Round 2

**Estado:** `P01_ROUND_2_READY`

**Fecha:** 30 de agosto de 2026

**Ronda:** `P01_R2`

**Dataset futuro:** `REAL_DEVELOPMENT`

**Participante permitido:** `P01`

## Versiones congeladas

| Componente | Versión |
|---|---|
| Engine | `1.1.0` |
| Parser | `rules-v0.1.0+explicit-v0.4.0+context-v0.2.0+safety-v0.2.0` |
| Schema de operación | `operation-v0.1.0` |
| Migración DB | `003_pilot_round_id` |
| Piloto | `pilot-v0` |
| UI | `pilot-ui-v0` |
| Consentimiento | `pilot-consent-v1` |
| Commit desplegado | `519ba141c15123023f24afed3efe0ae31dabab02` |

El tratamiento de datos no cambió, por lo que se mantiene el consentimiento v1. Sí cambió el instrumento técnico; por eso R2 tiene Engine 1.1 y `round_id` propio.

## Hashes del motor

Los siete hashes del motor coinciden con [`GENERALIZATION_ENGINE_LOCK.md`](GENERALIZATION_ENGINE_LOCK.md). La migración `003_pilot_round_id.sql` tiene SHA-256 `46fedf6b0b7a185d889d1359d63216ed5f639675223f8d1b75d8ee6ae3a53e9f`.

## Estado inicial de datos

- Integridad SQLite: `ok`.
- Migraciones: `001_initial`, `002_pilot_v0`, `003_pilot_round_id`.
- `P01_R1`: 2 sesiones, 71 eventos, Engine 1.0.
- `P01_R2`: 0 sesiones, 0 eventos, 0 inputs.
- Sesiones abiertas: 0.
- Tokens activos previos al primer acceso R2: 0.
- DB compartida con separación explícita por `round_id`; no se borró ni copió R1.

## Transporte y acceso

- URL: `https://129-80-183-35.sslip.io`.
- Certificado válido y renovación simulada exitosa.
- Credenciales rotadas y root-only; no se registran valores aquí.
- API y web activos; puertos internos no públicos.

## Condición de congelación

Desde el primer consentimiento válido de R2 no modificar reglas, parser, safety, contexto, normalización, extracción o clasificación hasta cerrar la ronda. Registrar errores y agrupar causas; no hacer `input → patch → input`.

## Protocolo inmediato

P01 usa lenguaje normal, no intenta engañar ni ayudar al parser, revisa cada propuesta y elige confirmar, corregir, rechazar o cancelar. Objetivo: 30 operaciones reales válidas como mínimo, preferibles 50–100 en varios momentos, sin inventar actividad para completar cuota.
