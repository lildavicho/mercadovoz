# Backup y recuperación — `pilot-v0`

## Estado

El código está preparado; no existe todavía volumen remoto ni backup verificado. Este punto permanece externo y bloquea P01.

Railway documenta backups manuales/programados para cualquier volumen, incluido SQLite: diarios retenidos 6 días, semanales 1 mes y mensuales 3 meses. Los snapshots son incrementales; borrar el volumen borra también sus backups y la restauración solo funciona en el mismo proyecto/entorno. Fuente: [Railway — Backups](https://docs.railway.com/volumes/backups).

## Política mínima

1. Volumen persistente en `/data`, una sola réplica.
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
