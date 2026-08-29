# Decisiones — Piloto privado

## 2026-08-29 — Congelar interpretación

- **Contexto:** el benchmark técnico pasó, pero aún no existe evidencia humana.
- **Opciones:** corregir cada error durante campo; versionar por ronda; introducir LLM.
- **Decisión:** `engine 1.0.0` queda congelado durante P01 Round 1. Los errores se registran y solo se consideran cambios generalizables después del lock de ronda.
- **Razón:** evita que cada nueva frase cambie el instrumento que se evalúa.
- **Trade-off:** errores conocidos durante la ronda no se corrigen de inmediato.
- **Reversible:** sí, mediante una nueva versión después de cerrar la ronda.
- **Evidencia:** [`PILOT_ENGINE_LOCK.md`](../pilot/PILOT_ENGINE_LOCK.md).

## 2026-08-29 — Persistencia mínima

- **Contexto:** P01 necesita persistencia privada y auditable; no hay necesidad demostrada de escala multiinstancia.
- **Opciones:** SQLite con volumen; PostgreSQL/Supabase; archivos JSONL.
- **Decisión:** SQLite WAL, migraciones versionadas y una sola instancia para `pilot-v0`.
- **Razón:** menor superficie operativa y cero dependencia de un convenio; JSONL preserva portabilidad.
- **Trade-off:** no permite réplicas concurrentes ni alta disponibilidad.
- **Reversible:** sí.
- **Evidencia:** [`ADR-004-sqlite-pilot.md`](ADR-004-sqlite-pilot.md).

## 2026-08-29 — Acceso privado

- **Contexto:** no se debe crear un sistema empresarial de usuarios.
- **Opciones:** contraseña en frontend; cuentas propias; protección del proveedor + invitaciones del backend.
- **Decisión:** protección del proveedor y códigos individuales solo como secreto de servidor; los tokens efímeros se guardan con hash.
- **Razón:** defensa en profundidad sin identidad real dentro del corpus.
- **Trade-off:** cerrar o refrescar exige una nueva invitación; deliberado para `pilot-v0`.
- **Reversible:** sí.

## 2026-08-29 — Hosting preparado, no ejecutado

- **Contexto:** el frontend es Next.js; la API necesita proceso persistente y volumen.
- **Opciones:** todo en Vercel; Vercel + Railway; Supabase/Postgres; servidor propio.
- **Decisión:** preparar Vercel para frontend y Railway para API/SQLite singleton.
- **Razón:** encaja sin reescribir persistencia ni crear otra base.
- **Trade-off:** dos proveedores y costo mínimo por verificar.
- **Reversible:** sí.

**Estado posterior:** supersedida antes de cualquier despliegue por ADR-005. No se creó proyecto, plan ni dato remoto en Vercel/Railway.

## 2026-08-29 — Target Oracle Cloud

- **Contexto:** el repositorio público debe quedar listo para un host persistente ARM64 y un flujo operacional simple.
- **Opciones:** conservar Vercel/Railway; Oracle Cloud singleton; PostgreSQL administrado.
- **Decisión:** preparar Oracle Cloud Ampere A1 Flex, Ubuntu 24.04 ARM64, Nginx, PM2, systemd y SQLite WAL.
- **Razón:** un único host persistente encaja con el piloto y la restricción singleton sin introducir otra base.
- **Trade-off:** el operador asume parches, TLS, firewall, backup y ventanas de mantenimiento.
- **Reversible:** sí; JSONL y migraciones preservan portabilidad.
- **Evidencia:** [`ADR-005-oracle-deployment.md`](ADR-005-oracle-deployment.md).

## Gates

- `VOICE_HOLD`: no hay evidencia humana de fricción de escritura.
- `LLM_HOLD`: no hay clase de error real que justifique complejidad.
- `OFFLINE_HOLD`: dependencias documentadas; sin offline completo.
- `PRIVATE_PILOT_READY_TO_DEPLOY`: preparación local aprobada; faltan acciones externas.
