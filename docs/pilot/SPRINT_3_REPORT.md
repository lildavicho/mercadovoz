# Sprint 3 — reporte de preparación del piloto privado

> Registro histórico: el target Vercel/Railway descrito aquí fue supersedido antes de desplegar por [`ADR-005`](../decisions/ADR-005-oracle-deployment.md). No se reescriben los resultados técnicos de Sprint 3.

**Fecha:** 29 de agosto de 2026  
**Resultado:** `PRIVATE_PILOT_READY_TO_DEPLOY`  
**Parada:** `EXTERNAL_ACTION_REQUIRED`

1. **Cambios:** motor congelado; acceso, consentimiento, sesiones, eventos, correcciones, outcomes, métricas, export, eliminación, UI privada y configuración de deploy.
2. **Arquitectura:** Next.js protegido → FastAPI singleton → engine 1.0.0 → SQLite WAL en volumen; operación y auditoría se confirman en una transacción.
3. **Tests:** 47/47 Python, TypeScript y Next production build; 0 vulnerabilidades npm; E2E móvil crítico sin errores.
4. **Seguridad:** secretos solo server-side, token hash, allowlist CORS, rutas dev ocultas, headers/noindex, input server-side, logs sin texto financiero.
5. **Privacidad:** mínimos necesarios, pseudónimos, sin cédula/teléfono/dirección/audio/ubicación, política de 90 días y eliminación documentada.
6. **Persistencia:** migraciones reproducibles, FK/checks/unique, aislamiento por participante, singleton y rollback probado.
7. **Instrumentación:** eventos relevantes y métricas `pilot-metrics-v1`; human outcome separado de predicción.
8. **Export:** script JSONL/CSV `real-development-v1`, hash SHA-256 y lock solo al cerrar ronda real.
9. **UX móvil:** acceso → consentimiento → escritura → tarjeta → corrección/rechazo/cancelación/confirmación → historial/audit → feedback/cierre; 375/390/430 px y desktop.
10. **Target:** Vercel frontend + Railway API/SQLite con volumen `/data`; no Supabase todavía.
11. **Costos:** `$0` local; Vercel Hobby condicionado a uso personal/no comercial o Pro `$20`; Railway desde Free/Hobby mínimo publicado; verificar antes de pagar.
12. **Pendiente externo:** `railway login`, enlazar ambos proyectos, volumen, secretos, URLs, protección Vercel, primer Docker build remoto y restore drill.
13. **Despliegue:** pasos y variables exactos en [`PILOT_READINESS.md`](PILOT_READINESS.md) y [`DEPLOYMENT_CHECKLIST.md`](../deployment/DEPLOYMENT_CHECKLIST.md).
14. **Gates:** técnico GO; piloto listo para desplegar; campo pendiente; voz/LLM/offline HOLD; cero participantes y cero registros reales.

No se creó Git, commit, tag, push, cuenta, plan, dominio ni deployment. No se creó `REAL_DEVELOPMENT_LOCK.md` ni `P01_ROUND1_REPORT.md` porque no existe una ronda real que congelar.
