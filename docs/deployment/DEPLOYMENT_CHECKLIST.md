# Checklist de despliegue privado — P01_R2

**Fecha:** 30 de agosto de 2026

**Resultado:** `PASS`

**Gate:** `P01_ROUND_2_READY`

- [x] 63/63 pruebas Python en Oracle
- [x] 3/3 pruebas frontend
- [x] TypeScript y production build
- [x] `npm audit --omit=dev`: 0 vulnerabilidades
- [x] CI de `main` verde
- [x] `.env.example` sin secretos; `.env` retirado del checkout
- [x] variables reales root-only en `/etc/mercadovoz/api.env`
- [x] credencial P01 y token operador rotados sin mostrarlos
- [x] migraciones `001`, `002` y `003`
- [x] R1 preservado como `P01_R1`; R2 configurado como `P01_R2`
- [x] acceso anterior revocado; 0 tokens activos antes de P01_R2
- [x] consentimiento `pilot-consent-v1` vigente
- [x] persistencia transaccional, idempotencia y aislamiento probados
- [x] export R1 fuera de Git, archivos `0600`, hashes congelados
- [x] backup predeploy íntegro fuera del checkout
- [x] Nginx expone solo 80/443; API/web escuchan en loopback
- [x] HTTP redirige a HTTPS
- [x] certificado válido y renovación `--dry-run` exitosa
- [x] CSP, `nosniff`, no framing, no referrer y `X-Robots-Tag`
- [x] rutas dev/documentación ocultas en modo piloto
- [x] health y config sin secretos
- [x] móvil 390×844 sin overflow; labels/password/focus semánticos
- [x] invitación inválida rechazada sin mostrar consentimiento o datos
- [x] systemd API, PM2 web y Nginx activos
- [x] rollback y stash previo disponibles
- [x] Engine 1.1 y lock de inicio R2 documentados

## Primer paso humano

Recuperar localmente la credencial P01 desde el archivo root-only documentado en [`P01_ROUND_2_ACCESS.md`](../pilot/P01_ROUND_2_ACCESS.md), abrir la URL HTTPS desde el móvil, aceptar el consentimiento y registrar una operación real normal. No pegar la credencial en chats, Git, issues o capturas.
