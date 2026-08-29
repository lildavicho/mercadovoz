# MercadoVoz

[![CI](https://github.com/lildavicho/mercadovoz/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/lildavicho/mercadovoz/actions/workflows/ci.yml)

MercadoVoz es un cuaderno operativo móvil que transforma lenguaje natural en propuestas de ventas, gastos, cuentas por cobrar y abonos. Está pensado inicialmente para comercios pequeños de Cuenca, Ecuador, que hoy dependen de cuadernos, memoria o notas informales y necesitan registrar rápido sin permitir que el software invente una transacción financiera.

```text
Natural language
  → interpretation
  → safety + explicit context
  → human confirmation or correction
  → idempotent save + audit trail
```

## Estado

| Gate | Estado |
|---|---|
| Technical benchmark | `TECHNICAL_GO` |
| Private pilot | `PRIVATE_PILOT_READY_TO_DEPLOY` |
| Field validation | `PENDING_REAL_DATA` |
| Voice | `VOICE_HOLD` |

No existen participantes ni métricas de precisión con usuarios reales. El corpus externo de Cuenca/Ecuador deriva de evidencia pública y permanece separado de los futuros datasets humanos.

## Operaciones core

- `SALE`
- `EXPENSE`
- `RECEIVABLE`
- `PAYMENT_RECEIVED`

Toda interpretación financiera requiere confirmación explícita. El motor detecta operaciones compuestas, pide contexto cuando falta una referencia material y conserva correcciones estructuradas.

## Arquitectura

```text
Browser
  ↓
Next.js mobile-first UI
  ↓ HTTPS
FastAPI private API
  ↓
Frozen Interpretation Engine
  ├─ safety rules
  ├─ explicit context
  ├─ correction workflow
  └─ confirmation gate
  ↓
SQLite WAL + audit/evaluation events
```

- Frontend: Next.js 16, React 19 y TypeScript.
- Backend: FastAPI y Python 3.11+.
- Persistencia de piloto: SQLite WAL, migraciones versionadas y una sola instancia.
- Destino preparado: Oracle Cloud Ampere A1 Flex, Ubuntu 24.04 ARM64, Nginx, PM2 y systemd.

Consulta [la arquitectura](docs/architecture/ARCHITECTURE.md) y [el despliegue Oracle](docs/deployment/ORACLE.md).

## Aspectos técnicos

- NLP financiero conservador y determinista;
- interpretación con contexto explícito y caducidad;
- human-in-the-loop antes de persistir;
- detección de operaciones compuestas y aproximaciones;
- confirmación idempotente y transacciones operación+auditoría;
- motor de correcciones estructuradas;
- datasets separados por provenance;
- prevención de leakage y evaluación reproducible;
- UX móvil para acceso, consentimiento y registro privado.

## Repositorio

- `apps/web`: frontend Next.js.
- `apps/api`: entrada y configuración FastAPI.
- `engine`: paquete Python, schemas y migraciones.
- `tests`: integración, regresión, evaluación y protocolo E2E.
- `research`: benchmarks públicos/sintéticos y provenance.
- `docs`: arquitectura, ADRs, evaluación, piloto, deployment y producto.
- `scripts`: evaluación, export privado, backup y operación.
- `data`: únicamente instrucciones; los datos runtime viven fuera de Git.

Árbol detallado: [REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md).

## Desarrollo local

```powershell
python -m pip install -e ".[api]"
python -m unittest discover -s tests -v

Set-Location apps\web
npm ci
npm run typecheck
npm run build
```

La ejecución privada requiere variables de `.env.example`. No utilices valores de piloto en archivos versionados.

## Evidencia y límites

El benchmark técnico congelado obtuvo 11/11 intenciones explícitas, 40/44 campos, 3/3 compuestos y cero violaciones monetarias críticas en el held-out independiente limpio. Es una muestra web-derived pequeña, no accuracy de campo.

Los datos `REAL_DEVELOPMENT` y `REAL_HELDOUT`, bases, audio, exports y mapeos de identidad nunca se versionan. Consulta [research/README.md](research/README.md) y [SECURITY.md](SECURITY.md).

## Licencia

Copyright © 2026 David Mendez. All rights reserved. La decisión de licencia open source permanece pendiente; este repositorio público no concede permiso de reutilización comercial.
