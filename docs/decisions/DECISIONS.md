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

## 2026-08-30 — Engine 1.1.0 después de evidencia manual

- **Contexto:** cinco fallos P0 reproducibles mostraron contaminación producto/precio, centavos omitidos, pronombre como cliente y colapso de ventas repetidas. Oracle ya contiene datos reales bajo `1.0.0`.
- **Opciones:** parchear frases; modificar el parser legado; introducir LLM; añadir una gramática estructurada acotada antes del parser congelado.
- **Decisión:** mantener `rules-v0.1.0` byte a byte, publicar el candidato `engine 1.1.0` con `explicit-v0.4.0` y `safety-v0.2.0`, y bloquear su despliegue hasta cerrar/hashear la ronda activa.
- **Razón:** resuelve familias lingüísticas y añade abstención defensiva sin reescribir el baseline ni mezclar versiones de campo.
- **Trade-off:** el esquema sigue sin line items y algunas permutaciones terminan no finales.
- **Reversible:** sí; Oracle continúa en `1.0.0` y el rollback queda por commit/lock.
- **Evidencia:** [`GENERALIZATION_REPORT_2026-08-30.md`](../evaluation/GENERALIZATION_REPORT_2026-08-30.md) y [`GENERALIZATION_ENGINE_LOCK.md`](../pilot/GENERALIZATION_ENGINE_LOCK.md).

## 2026-08-30 — HTTP temporal e idempotencia

- **Contexto:** `crypto.randomUUID()` no está disponible en todos los contextos HTTP; el ajuste directo de Oracle introdujo recursión accidental.
- **Decisión:** usar `randomUUID` cuando existe, `getRandomValues` como fallback y una clave local distinta de último recurso; servir API same-origin cuando no se configura URL.
- **Razón:** evita crash o duplicación por reintentos durante pruebas temporales sin hardcodear secretos.
- **Trade-off:** HTTP continúa siendo solo testing y no habilita campo real.
- **Reversible:** sí; HTTPS sigue siendo el destino obligatorio.

## 2026-08-30 — Cierre y separación explícita de rondas P01

- **Contexto:** Oracle contenía 25 inputs reales de P01 bajo Engine 1.0, sin outcomes terminales, mientras Engine 1.1 estaba listo localmente.
- **Opciones:** borrar la prueba; reinterpretarla como R2; inferir outcomes; cerrar administrativamente, exportar y congelar R1 antes de desplegar otra versión.
- **Decisión:** preservar la captura como `P01_R1 / REAL_DEVELOPMENT / engine 1.0.0`, cerrar las sesiones abandonadas mediante evento auditable, revocar accesos, congelar hashes y añadir `round_id` persistido antes de `P01_R2`.
- **Razón:** mantiene la validez histórica y evita mezclar versiones o atribuir acciones al participante.
- **Trade-off:** R1 no permite medir éxito ni precisión humana y su utilidad queda limitada a pipeline y análisis técnico.
- **Reversible:** el código de migración sí; la evidencia congelada no se reescribe.
- **Evidencia:** [`P01_ROUND_1_LOCK.md`](../pilot/P01_ROUND_1_LOCK.md) y [`P01_ROUND_1_EVALUATION.md`](../evaluation/P01_ROUND_1_EVALUATION.md).

## 2026-08-30 — Gate después de P01_R1

- **Contexto:** el replay de R1 con Engine 1.1 no detectó regresiones financieras críticas, pero R1 carece de ground truth humano.
- **Decisión:** `FIELD_ITERATE`, `VOICE_HOLD`, `LLM_HOLD`; Engine 1.1 solo puede abrir una ronda nueva después de HTTPS, rotación de acceso y lock de inicio.
- **Razón:** la próxima incertidumbre es obtener outcomes humanos seguros, no añadir más inteligencia.
- **Trade-off:** no se atribuyen mejoras semánticas a cambios técnicamente plausibles sin aceptación/corrección real.
- **Reversible:** sí, mediante otro gate después de R2.
- **Evidencia:** [`P01_R1_REPLAY_ENGINE_1_1.md`](../evaluation/P01_R1_REPLAY_ENGINE_1_1.md).

## 2026-08-30 — Una DB con `round_id` explícito

- **Contexto:** R1 debe conservar relaciones/auditoría y R2 no puede confundirse por fechas o versión implícita.
- **Opciones:** DB nueva; tablas por ronda; misma DB con identificador obligatorio.
- **Decisión:** mantener SQLite singleton y añadir `round_id` obligatorio en sesión/evento, con backfill versionado de R1.
- **Razón:** separación consultable y migración reversible sin duplicar infraestructura ni borrar historia.
- **Trade-off:** consultas operativas deben filtrar ronda cuando comparan evaluación; la frontera de participante sigue siendo independiente.
- **Reversible:** sí para rondas futuras; el backfill histórico queda auditado.
- **Evidencia:** [`P01_ROUND_2_START.md`](../pilot/P01_ROUND_2_START.md).

## 2026-08-30 — HTTPS gratuito para P01

- **Contexto:** no existe dominio propio y HTTP no es aceptable para credenciales o texto real.
- **Opciones:** comprar dominio; túnel/proveedor; hostname IP de `sslip.io` con Let's Encrypt.
- **Decisión:** usar `129-80-183-35.sslip.io`, certificado Let's Encrypt y renovación Certbot para la ronda privada.
- **Razón:** habilita HTTPS válido sin cuenta o compra y mantiene un único origen.
- **Trade-off:** dependencia DNS externa y nombre ligado a la IP; debe migrarse antes de ampliar el piloto.
- **Reversible:** sí.
- **Evidencia:** [`HTTPS_DEPLOYMENT.md`](../deployment/HTTPS_DEPLOYMENT.md).

## 2026-08-30 — Consentimiento v1 permanece

- **Contexto:** Engine y ronda cambian, pero datos recolectados, propósito, retención y derechos no cambian.
- **Decisión:** conservar `pilot-consent-v1` y registrar un nuevo consentimiento al iniciar R2.
- **Razón:** versionar por cambios reales del acuerdo, no por cada deploy técnico.
- **Trade-off:** el lock de ronda debe declarar por separado el Engine nuevo.
- **Reversible:** sí mediante `consent-v2` antes de cualquier cambio de tratamiento.
