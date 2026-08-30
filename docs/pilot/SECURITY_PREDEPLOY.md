# Auditoría de seguridad — P01_R2

**Resultado:** `PASS_WITH_RESIDUAL_RISK`

**Verificado:** 30 de agosto de 2026 sobre Oracle y red externa

| Área | Evidencia | Resultado |
|---|---|---|
| transporte | HTTP 301 a HTTPS; certificado ECDSA Let's Encrypt válido hasta 2026-11-28 | PASS |
| renovación | timer activo y `certbot renew --dry-run --no-random-sleep-on-renew` exitoso | PASS |
| secretos | variables y credencial operador en `/etc/mercadovoz`, root-only `0600` | PASS |
| checkout | `.env` anterior destruido; exports movidos fuera del árbol Git | PASS |
| rotación | acceso P01 y token operador distintos; registro operador coincide con env | PASS |
| sesiones previas | 9 accesos revocados; 0 tokens activos antes de R2 | PASS |
| corpus/fixtures | no servidos por web/API; exports privados fuera de Git | PASS |
| rutas dev | documentación y endpoints de laboratorio ocultos en `pilot` | PASS |
| logs | estructurados; no registran texto financiero completo | PASS |
| dependencias | 63 pruebas; 3 web; audit 0; typecheck/build/CI | PASS |
| validación | Pydantic/servidor, SQL parametrizado, React sin HTML inyectado | PASS |
| CSRF/CORS | bearer sin cookie ambient; origin HTTPS exacto | PASS |
| cabeceras | CSP, `nosniff`, DENY/frame-ancestors, no-referrer, permisos sensibles off | PASS |
| indexación | `X-Robots-Tag: noindex, nofollow, noarchive` | PASS |
| red | 3000/8000 loopback; UFW/iptables admiten 22,80,443 | PASS limitado |
| autorización | participante deriva del token; sesión y datos se filtran por participante | PASS |
| rate limit | 10 intentos/5 min por proceso singleton | PASS limitado |

## Riesgo residual

El nombre `sslip.io` depende de un servicio DNS externo gratuito y no equivale a dominio propio. Los códigos de invitación no son identidad fuerte. SQLite no cifra el archivo en reposo y el backup depende de permisos del host. El rate limit vive en memoria. La instancia sigue requiriendo parches y vigilancia operacional. No se afirma GDPR, ISO 27001, SOC 2 ni otra certificación.

El certificado se emitió mediante HTTP-01 y Nginx; Certbot administra su instalación y renovación según su [guía oficial](https://eff-certbot.readthedocs.io/en/stable/using.html). `sslip.io` resuelve el hostname con la IP incorporada y admite certificados individuales, según la [documentación del servicio](https://sslip.io/).
