# Lock de P01 Round 1

**Lock:** `P01_R1_REAL_DEVELOPMENT_v1`  
**Participante:** `P01`  
**Ronda:** `P01_R1`  
**Motor de captura:** `1.0.0`  
**Fecha de cierre:** 30 de agosto de 2026  
**Estado:** `FROZEN`

## Declaración

Los 25 inputs y 71 eventos fueron exportados reproduciblemente después de cerrar administrativamente dos sesiones abandonadas y revocar nueve sesiones de acceso. No se editó ni eliminó evidencia. Cualquier corrección futura debe producir una versión nueva y conservar estos hashes.

## Hashes SHA-256

| Artefacto privado | Registros | SHA-256 |
|---|---:|---|
| `p01-r1-real-development.jsonl` | 25 | `ba1ff8a70210a287a8f6d78d4c7b2aa75a84172f4400102155574d3071b0efa7` |
| `p01-r1-events.csv` | 71 | `8997952de71965db88f5802fd8292cdbf8e3fb6244aac2eb9b9c88c29e3c80ed` |
| `p01-r1-summary.json` | — | `d78a77cea8ea431d28e756082063c6b4446ba792ef692da250c27f863a97854b` |
| `p01-r1-manifest.json` | — | `229932792ff1aad1f4e990b20df37f74498da7eb3b6a9947f38a26cb49b92c6d` |
| `P01_R1_REPLAY_ENGINE_1_1.json` | 25 | `338d9758c00261bd15a2e8032834d3d7d362153ed033e8b23f7afc4e9e83b028` |

Los archivos privados no se versionan en Git. El manifest registra `P01`, `P01_R1`, `REAL_DEVELOPMENT`, dos sesiones, versiones únicas, fechas, conteos y `real_interview=false`.

## Backup pre-cierre

- Ruta privada del servidor: `/home/ubuntu/backups/mercadovoz/p01-round1-preclose-20260830-065049.db`.
- SHA-256: `4c74bac5b00010b96b78af31e1f594960e49902b5c183c2f0b0f1644c10cb974`.
- `PRAGMA integrity_check`: `ok`.
- Migraciones presentes al crear el backup: `001_initial`, `002_pilot_v0`.

## Exclusiones y límites

- No existen operaciones confirmadas ni correcciones estructuradas.
- Los cierres de sesión son administrativos, no outcomes del participante.
- No existe entrevista real asociada.
- El replay 1.1 es un artefacto técnico separado.
- P01 no puede convertirse en held-out después de ser observado.

## Inmutabilidad

Este documento congela la versión 1. Los exports se conservan con permisos privados y sus originales no deben regenerarse silenciosamente. Una transformación, anonimización adicional o corrección requiere sufijo/versionado nuevo, nuevo manifest y hashes nuevos, con referencia explícita a este lock.
