# Rollback del piloto

## Detener acceso

1. Activar protección total o pausar el frontend.
2. Revocar/rotar `MERCADOVOZ_PILOT_ACCESS_CODES` y `MERCADOVOZ_OPERATOR_TOKEN`.
3. Detener el servicio API después de confirmar que no hay sesión activa.
4. No borrar volumen, backups ni exports durante el incidente.

## Revertir aplicación

- Vercel: seleccionar el último deployment verificado y usar rollback/instant rollback.
- Railway: redeploy de la imagen/configuración anterior sin cambiar el volumen.
- Confirmar que `ENGINE_VERSION` sigue igual al lock y que `/health` no expone configuración.

## Revertir datos

1. Exportar el estado actual con timestamp y hash.
2. Restaurar un backup del volumen solo después de revisar el punto objetivo.
3. Validar migraciones, conteos, una operación sintética y export.
4. Registrar registros perdidos/recuperados; nunca mezclar el export previo con el restaurado como una sola ronda.

## Reanudar

Reabrir acceso solo tras tests, build, health, aislamiento, idempotencia, backup y revisión de incidente. Si el motor cambia, cerrar la ronda y emitir nueva versión; no continuar P01 Round 1 con dos motores.
