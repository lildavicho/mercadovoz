# Checklist de despliegue privado

## Local completado

- [x] 47/47 tests
- [x] TypeScript
- [x] production build
- [x] `.env.example` sin secretos
- [x] migraciones `001` y `002`
- [x] acceso, consentimiento y aislamiento
- [x] persistencia transaccional e idempotencia
- [x] auditoría y export `REAL_DEVELOPMENT`
- [x] headers, CORS, validación y rutas dev ocultas
- [x] móvil 375/390/430 y escritorio sin overflow
- [x] procedimiento de rollback
- [x] `PILOT_ENGINE_LOCK.md`

## Acción externa pendiente

- [ ] Crear Oracle Ampere A1 Flex ARM64 y restringir SSH al CIDR administrador
- [ ] Clonar `main` en `/home/ubuntu/apps/mercadovoz`
- [ ] Crear `/etc/mercadovoz/api.env` root-only y directorio runtime
- [ ] Configurar `NEXT_PUBLIC_API_URL=https://HOST/api` y CORS exacto
- [ ] Ejecutar tests, typecheck, build y migraciones en ARM64
- [ ] Activar FastAPI/systemd y Next.js/PM2 como singletons
- [ ] Configurar Nginx y HTTPS; no exponer 3000/8000
- [ ] Activar backup diario/semanal y completar restore drill
- [ ] Comprobar que `/api/docs`, `/api/openapi.json` y `/api/interpret` dev responden 404
- [ ] Ejecutar prueba sintética completa desde móvil real y luego limpiar esos datos
- [ ] Confirmar logs sin texto financiero ni secretos
- [ ] Congelar URL/versiones finales antes de consentimiento real

P01 no comienza hasta completar todas las casillas externas.
