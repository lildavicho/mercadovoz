# Pilot readiness — MercadoVoz `P01_R2`

**Gate:** `P01_ROUND_2_READY`

**Campo:** `PENDING_REAL_OUTCOMES`

**URL:** `https://129-80-183-35.sslip.io`

## Arquitectura desplegada

```text
Nginx + HTTPS / acceso por invitación
  → Next.js pilot-ui-v0 en 127.0.0.1:3000
  → FastAPI en 127.0.0.1:8000
  → Engine 1.1.0 congelado para P01_R2
  → SQLite WAL singleton + migraciones 001–003
  → exports y backups privados fuera de Git
```

Una confirmación guarda operación y auditoría en la misma transacción. Reintentos con la misma clave son idempotentes. Las propuestas viven en memoria: un reinicio puede descartarlas, pero no crea una operación.

## Integridad de rondas

- `P01_R1`: Engine 1.0, 25 inputs y 71 eventos congelados, sin outcomes terminales.
- `P01_R2`: Engine 1.1, 0 sesiones y 0 eventos al abrir el gate.
- `round_id` existe en sesiones/eventos; migración 003 backfilló R1 por sesión.
- Se usa la misma DB para preservar relaciones y auditoría; la separación es explícita y consultable, no inferida por fecha.

## Privacidad, consentimiento y acceso

Se mantiene `pilot-consent-v1`: la finalidad y el tratamiento no cambiaron. La credencial P01 y el token operador fueron rotados y solo existen fuera de Git. No se solicita identidad legal, teléfono, dirección, ubicación, foto ni audio. El primer acceso válido de R2 debe crear consentimiento y sesión; no se realizó smoke sintético con una credencial real.

## Verificación

- 63 pruebas Python, 3 pruebas web, TypeScript, build, audit y CI: PASS.
- Benchmarks: 11/11 intención y 40/44 campos held-out externo limpio; 3/3 compuestos; 0/4 violaciones críticas. Externo completo: 69/85, 199/290, 25/25 y 0/67.
- Replay R1 con Engine 1.1: 25 registros y 0 violaciones críticas; accuracy humana `NOT_MEASURABLE`.
- HTTPS externo, redirección, health, config, cabeceras y renovación: PASS.
- Navegador móvil 390×844: sin overflow; acceso inválido rechazado; no aparecen corpus, texto original ni consentimiento protegido.

## Rollback

Backup predeploy: `/home/ubuntu/backups/mercadovoz/p01-r2-predeploy-20260830T070752Z.db`, SHA-256 `2ed12c94d0a6408748dfccf18d56e524ea4cd66dfbab0def4df1e785e4ca745f`, integridad `ok`. El servidor conserva `stash@{0}` con los hotfixes anteriores ya integrados en Git. Ver [`ROLLBACK.md`](../deployment/ROLLBACK.md).

## Gates

| Gate | Estado |
|---|---|
| técnico | `TECHNICAL_GENERALIZATION_GO` |
| despliegue privado | `HTTPS_LIVE_PRIVATE_ACCESS` |
| inicio R2 | `P01_ROUND_2_READY` |
| campo | `PENDING_REAL_OUTCOMES` |
| voz | `VOICE_HOLD` |
| LLM | `LLM_HOLD` |
| offline | `OFFLINE_HOLD` |

El siguiente paso permitido es uso normal de P01 con consentimiento. No se autoriza marketing, acceso masivo, voz, LLM ni claims de validación.
