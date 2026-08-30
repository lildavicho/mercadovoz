# Lock de inicio — P01 Round 3

**Estado:** `P01_R3_READY_NOT_STARTED`

**Engine:** `1.2.0`

**Parser:** `rules-v0.1.0+explicit-v0.5.0+context-v0.2.0+safety-v0.2.0`

**Schema:** `operation-v0.2.0`; SQLite migrations `001`–`004`

**Release commit desplegado:** `2f5a570df11d3ae41e8cfc55208d28717b8cc739`

**Consentimiento:** `pilot-consent-v1`

**Hostname:** `https://129-80-183-35.sslip.io`

**Flags:** `NEXT_PUBLIC_BATCH_EXPERIMENT=false`, `MERCADOVOZ_BATCH_EXPERIMENT=false` por default/ruta ausente, `NEXT_PUBLIC_VOICE_EXPERIMENT=false`

**Persistencia:** mismo SQLite WAL del piloto, migración aditiva; R1/R2 no se reescribieron. Backup predeploy externo al checkout: `mercadovoz-20260830T203450Z.sqlite`, SHA-256 `3007016d779699be402e07e8396c5f0c7f60daf4a888a15284888803c368b6f4`.

**Preparado:** 30 de agosto de 2026; credencial rotada a las `20:37:09 UTC`, deployment verificado después de las `20:39 UTC`.

## Verificación inicial

- `/health`: aplicación y base `ok`.
- `/pilot/config`: Engine 1.2.0, schema operation-v0.2.0, round P01_R3.
- DB: integrity `ok`; 4 sesiones históricas, 148 eventos y 3 operaciones preservados.
- P01_R3: 0 sesiones, 0 inputs y 0 tokens activos antes del primer acceso.
- Batch API: 404; UI batch ausente.
- Voice UI: ausente; permisos de micrófono deshabilitados por header.

Este lock no inicia la ronda. R3 comienza únicamente cuando P01 recupera la nueva credencial por el canal privado, entra, acepta consentimiento y crea una sesión real. No usar datos fabricados para probar ese acceso.
