# Estado de MercadoVoz

**Actualizado:** 29 de agosto de 2026

| Campo | Estado |
|---|---|
| `TECHNICAL_STATUS` | `TECHNICAL_GO` |
| `FIELD_VALIDATION_STATUS` | `PENDING_REAL_DATA` |
| `PILOT_STATUS` | `PRIVATE_PILOT_READY_TO_DEPLOY` |
| `ENGINE_VERSION` | `1.0.0` (congelado) |
| `PILOT_VERSION` | `pilot-v0` |
| `CURRENT_PARTICIPANTS` | `0` |
| `REAL_DEVELOPMENT_RECORDS` | `0` |
| `REAL_HELDOUT_RECORDS` | `0` |
| `CRITICAL_ERRORS` | `0 observados`; aún no existe uso real |
| `LAST_GATE` | `LOCAL_PILOT_READINESS_PASS` |
| `NEXT_GATE` | `EXTERNAL_ACTION_REQUIRED: conectar despliegue privado y ejecutar P01 Round 1` |
| `REPOSITORY_STATUS` | `GITHUB_INITIALIZED` |
| `REPOSITORY_VISIBILITY` | `PUBLIC` |
| `DEFAULT_BRANCH` | `main` |
| `INTEGRATION_BRANCH` | `develop` |
| `DEPLOYMENT_STATUS` | `READY_FOR_ORACLE_DEPLOY` (no desplegado) |

## Qué está listo

- Motor y benchmark congelados en [`PILOT_ENGINE_LOCK.md`](PILOT_ENGINE_LOCK.md); no se modificaron reglas, parser, seguridad, contexto, normalización, extracción ni clasificación.
- Acceso por invitación, consentimiento explícito versionado, sesiones pseudónimas y separación `REAL_DEVELOPMENT`.
- Persistencia transaccional, aislamiento por participante, idempotencia, eventos de evaluación, métricas, exportación y eliminación.
- Interfaz móvil del flujo escribir → entender → corregir/rechazar/cancelar → confirmar → historial.
- Configuración reproducible para una sola instancia Oracle con Nginx, frontend Next.js bajo PM2, API FastAPI bajo systemd y SQLite persistente fuera de Git.
- Suite, tipos, build, seguridad de dependencias y E2E manual crítico verificados localmente.

## Qué no significa

`PRIVATE_PILOT_READY_TO_DEPLOY` no significa producción, validación comercial ni precisión con usuarios reales. Las pruebas visuales usaron una base sintética aislada y la eliminaron al terminar; no cuentan como participante ni como `REAL_DEVELOPMENT`.

## Bloqueo real

Hace falta una acción externa: crear y asegurar la instancia Oracle, cargar secretos fuera del repositorio, configurar HTTPS y verificar build/respaldo/restauración. No se desplegó y no se creó P01. Ver [`DEPLOYMENT_CHECKLIST.md`](../deployment/DEPLOYMENT_CHECKLIST.md).

## Gates posteriores

1. Despliegue privado verificado → iniciar P01 Round 1 con consentimiento real.
2. Cerrar 30 operaciones válidas como mínimo → congelar `REAL_DEVELOPMENT` y emitir decisión de campo.
3. Voz permanece en `VOICE_HOLD` hasta evidencia real de fricción al escribir o preferencia clara por voz.
