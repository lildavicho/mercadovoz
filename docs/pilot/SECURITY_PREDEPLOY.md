# Auditoría de seguridad pre-deploy — `pilot-v0`

**Resultado local:** `PASS_WITH_EXTERNAL_CHECKS`  
**Alcance:** código y artefactos locales; no certifica la configuración futura del proveedor.

## Hallazgos y controles

| Área | Verificación | Resultado |
|---|---|---|
| `.env*` | solo ejemplos sin secretos; variantes reales ignoradas | PASS |
| claves/tokens/DB URL | no aparecen valores reales versionados | PASS |
| cliente | recibe solo `NEXT_PUBLIC_API_URL` | PASS |
| invitaciones | secretos de servidor; tokens persistidos como SHA-256 | PASS |
| corpus/benchmarks/fixtures | no se copian al build web; rutas dev ocultas en `pilot` | PASS |
| docs/debug | `/docs`, OpenAPI y rutas de laboratorio devuelven 404 en `pilot` | PASS |
| errores | respuestas no exponen stack/configuración | PASS |
| logs | eventos estructurados; no registran texto financiero original | PASS |
| source maps | browser production source maps desactivados | PASS |
| dependencias frontend | `npm audit --omit=dev`: 0 vulnerabilidades | PASS |
| input | límites + validación Pydantic en servidor | PASS |
| SQL | parámetros SQLite, no concatenación de input | PASS |
| CORS | allowlist exacta, sin wildcard en piloto | PASS |
| XSS | React escapa texto; no existe HTML inyectado | PASS |
| CSRF | API usa bearer header, no cookie ambient authority | PASS |
| framing/referrer/MIME | CSP `frame-ancestors`, `Referrer-Policy`, `nosniff` | PASS |
| rate limit | 10 intentos de acceso/5 min por proceso | PASS limitado |
| autorización | participante derivado del token y comparado con sesión | PASS |

## Dependencias externas obligatorias

- Activar Vercel Authentication o protección equivalente para frontend.
- Mantener códigos y token de operador únicamente en secretos de Railway.
- Confirmar HTTPS en ambas URLs y establecer `MERCADOVOZ_ALLOWED_ORIGINS` a la URL exacta.
- Mantener una sola réplica; el rate limit es en memoria y no se comparte entre instancias.
- Railway requiere `RAILWAY_RUN_UID=0` para escribir en su volumen montado como root; verificar que el contenedor no expone shell ni rutas administrativas.
- Ejecutar el checklist desde una red externa antes de P01.

## Riesgo residual

Los códigos de invitación no son identidad fuerte. Para P01 son una barrera mínima adicional a la protección del proveedor; si el piloto se amplía o expone datos entre varias personas, migrar a autenticación administrada. No se afirma cumplimiento de GDPR, ISO, SOC 2 ni otra certificación.
