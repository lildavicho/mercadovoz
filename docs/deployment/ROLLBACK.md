# Rollback del piloto

## Detener acceso

1. Activar protección total o pausar el frontend.
2. Revocar/rotar `MERCADOVOZ_PILOT_ACCESS_CODES` y `MERCADOVOZ_OPERATOR_TOKEN`.
3. Detener el servicio API después de confirmar que no hay sesión activa.
4. No borrar volumen, backups ni exports durante el incidente.

## Revertir aplicación

- En Oracle, comprobar que no hay sesión activa y crear backup consistente con hash.
- Detener API/web, volver al commit documentado mediante un checkout recuperable y reinstalar/build; no usar `reset --hard`.
- Restaurar la copia previa de Nginx solo si falla TLS y validar `nginx -t` antes de recargar.
- El stash `pre-engine-1.1-server-hotfixes` conserva la configuración anterior; no aplicarlo sobre código nuevo sin revisar conflictos.
- Confirmar que `ENGINE_VERSION` sigue igual al lock y que `/health` no expone configuración.

## Revertir datos

1. Exportar el estado actual con timestamp y hash.
2. Restaurar un backup del volumen solo después de revisar el punto objetivo.
3. Validar migraciones, conteos, una operación sintética y export.
4. Registrar registros perdidos/recuperados; nunca mezclar el export previo con el restaurado como una sola ronda.

## Reanudar

Reabrir acceso solo tras tests, build, health, aislamiento, idempotencia, backup y revisión de incidente. Si el motor cambia, cerrar la ronda y emitir nueva versión; no continuar una ronda con dos motores.
