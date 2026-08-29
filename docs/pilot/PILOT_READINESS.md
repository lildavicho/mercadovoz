# Pilot readiness — MercadoVoz `pilot-v0`

**Gate local:** `PRIVATE_PILOT_READY_TO_DEPLOY`  
**Bloqueo:** `EXTERNAL_ACTION_REQUIRED`  
**No iniciado:** P01, `REAL_DEVELOPMENT`, `REAL_HELDOUT`, voz.

## Arquitectura

```text
Vercel protegido / Next.js pilot-ui-v0
  → HTTPS + bearer token + X-Pilot-Session
Railway singleton / FastAPI
  → motor 1.0.0 congelado
  → transacción operación + auditoría
SQLite WAL / volumen /data
  → operacional | evaluación | audit | analytics
  → export JSONL versionado
```

Propuestas viven en memoria; operaciones confirmadas, eventos, consentimiento, feedback y sesiones persisten. Reiniciar antes de confirmar descarta la propuesta, no crea una operación. Railway no permite réplicas en servicios con volumen, lo que coincide con el requisito singleton de SQLite.

## Seguridad, privacidad y consentimiento

Ver [`SECURITY_PREDEPLOY.md`](SECURITY_PREDEPLOY.md), [`PRIVACY_MODEL.md`](PRIVACY_MODEL.md) y [`PILOT_CONSENT.md`](PILOT_CONSENT.md). Hay doble barrera: protección del frontend + invitación de participante. Todos los límites se validan en servidor. No se guarda identidad real ni audio.

## Persistencia e integridad

Migraciones `001_initial` y `002_pilot_v0`; FK, enums/checks, claves únicas, token hash, separación por participante y transacción operación/auditoría. Repetir confirmación devuelve la misma operación. SQLite exige una réplica.

## Instrumentación

Eventos relevantes: sesión, texto, interpretación, contexto, confirmación mostrada, corrección, confirmación, rechazo, cancelación, error y cierre. El original se conserva; la normalización vive separada. La acción humana es `USER_ACCEPTED_OPERATION`, no ground truth perfecto. Definiciones congeladas en [`PILOT_METRICS.md`](PILOT_METRICS.md).

## Export y eliminación

```powershell
python scripts\export\export_real_development.py --db C:\ruta\pilot.db --participant P01 --kind real-development --output C:\ruta-segura\p01-round1-v1.jsonl --csv
python scripts\pilot\pilot_admin.py --db C:\ruta\pilot.db metrics --participant P01
python scripts\pilot\pilot_admin.py --db C:\ruta\pilot.db delete-participant --participant P01 --confirm DELETE-P01
```

El export produce SHA-256. No crear `REAL_DEVELOPMENT_LOCK.md` hasta cerrar una ronda real; luego no editar silenciosamente, sino emitir v2.

## Testing local

- 47 tests Python: consentimiento, sesión, interpretación, confirmación, corrección, rechazo, cancelación, idempotencia, persistencia, rollback transaccional, auditoría, aislamiento, export, eliminación y seguridad financiera.
- TypeScript y build production pasan.
- `npm audit --omit=dev`: cero vulnerabilidades.
- E2E manual: identidad sintética acepta, envía venta, corrige monto/cantidad, confirma, ve historial/audit, da feedback y cierra; sin errores de navegador. La base y sus exports se eliminaron al terminar para no contaminarlos con `REAL_DEVELOPMENT`.
- Viewports: 375×812, 390×844, 430×932 y 1280×800; sin overflow.
- El Dockerfile de API no pudo construirse localmente porque Docker Desktop no tenía activo el engine Linux; no bloquea la instalación nativa prevista en Oracle, pero su build queda como check opcional pendiente.

## Proveedor recomendado

Una instancia Oracle Cloud `VM.Standard.A1.Flex` con Ubuntu 24.04 ARM64, 2 OCPU, 12 GB RAM y 50 GB de boot volume persistente. Nginx sirve un único origen HTTPS; PM2 mantiene Next.js y systemd mantiene FastAPI. Ver [`ORACLE.md`](../deployment/ORACLE.md) y ADR-005.

## Variables

API: `MERCADOVOZ_ENV=pilot`, `MERCADOVOZ_DB=/home/ubuntu/apps/mercadovoz/data/runtime/mercadovoz-pilot.db`, `MERCADOVOZ_PILOT_ACCESS_CODES`, `MERCADOVOZ_OPERATOR_TOKEN` y `MERCADOVOZ_ALLOWED_ORIGINS`. Web build: `NEXT_PUBLIC_API_URL=https://HOST/api`. Los secretos viven en `/etc/mercadovoz/api.env`, fuera de Git.

## Secuencia exacta de despliegue

1. Crear la instancia y restringir OCI NSG/SSH.
2. Clonar `main` en `/home/ubuntu/apps/mercadovoz`.
3. Instalar dependencias, ejecutar tests/typecheck/build.
4. Crear el environment root-only y el directorio runtime.
5. Activar FastAPI/systemd, Next.js/PM2 y Nginx.
6. Configurar HTTPS válido y no exponer 3000/8000.
7. Completar backup/restore y E2E sintético; limpiar la base.
8. Congelar URL/versiones antes de autorizar P01.

No pasar secretos en comandos, documentación, issues ni Git. La creación de OCI, DNS y el despliegue requieren una ejecución separada autorizada.

## Rollback y campo

Ver [`ROLLBACK.md`](../deployment/ROLLBACK.md), [`BACKUP_RECOVERY.md`](../deployment/BACKUP_RECOVERY.md) y [`FIELD_PROTOCOL.md`](FIELD_PROTOCOL.md).

## Limitaciones conocidas

Singleton; rate limit en memoria; propuestas no sobreviven restart; códigos no son identidad fuerte; SQLite no cifra el archivo; backups no están aún verificados; métricas dependen de anotación humana para critical errors; no existe validación de utilidad/demanda.

## Gates

| Gate | Estado |
|---|---|
| técnico | `TECHNICAL_GO` |
| preparación privada | `PRIVATE_PILOT_READY_TO_DEPLOY` |
| deploy | `EXTERNAL_ACTION_REQUIRED` |
| campo | `PENDING_REAL_DATA` |
| voz | `VOICE_HOLD` |
| LLM | `LLM_HOLD` |
| offline | `OFFLINE_HOLD` |
