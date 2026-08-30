# Backup y recuperación — `pilot-v0`

## Estado

Oracle usa un volumen local y SQLite WAL. El 30 de agosto de 2026 se creó un snapshot consistente mediante la API `sqlite3.Connection.backup`, se validó `PRAGMA integrity_check = ok` y se guardó checksum SHA-256 con permisos `0600` fuera del repositorio. Esto verifica creación e integridad de backup; una restauración completa en un entorno aislado sigue pendiente y no debe probarse sobre la base real activa.

Los scripts aceptan tanto el CLI `sqlite3` como el módulo estándar `sqlite3` de Python. La ausencia del CLI en Oracle ya no impide respaldar ni verificar integridad.

## Política mínima

1. Volumen persistente del host, una sola instancia de aplicación.
2. Backup diario y semanal antes de P01.
3. Export JSONL de evaluación y copia operacional cifrada al cerrar cada ronda.
4. No guardar exports en Git ni en el frontend.
5. Registrar fecha, tamaño, hash SHA-256 y custodio de cada export.

## Prueba obligatoria de restauración

1. Crear datos sintéticos marcados `SYNTHETIC_QA`.
2. Ejecutar backup manual.
3. Agregar un segundo registro sintético.
4. Restaurar el backup en el mismo entorno.
5. Verificar que el primero existe, el segundo no y `/health` responde sin secretos.
6. Volver a un volumen limpio antes de P01 y documentar evidencia.

No asumir que un backup existe hasta completar esta prueba. Para portabilidad fuera del proveedor, el lock de ronda debe incluir JSONL + hashes.
