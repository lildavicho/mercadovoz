# Baseline previo al motor batch

**Fecha:** 30 de agosto de 2026

**Rama de partida:** `develop`

**Commit:** `0950b8d4298624e2397d0bed60390d1690d0e586`

**Engine:** `1.1.0`

**Propósito:** fijar la evidencia reproducible antes de desarrollar el motor multioperación fuera de producción.

## Límite de evaluación

Este baseline no cambia ni reemplaza los locks de P01. `P01_R1` continúa congelado y `P01_R2` continúa asociado a Engine 1.1.0. Los resultados locales se guardaron únicamente bajo `data/runtime/batch-baseline/`, ruta ignorada por Git.

## Verificaciones

| Verificación | Resultado |
|---|---:|
| Pruebas Python | 63/63 |
| Pruebas web | 3/3 |
| TypeScript | correcto |
| Build Next.js de producción | correcto |
| Auditoría npm de dependencias de producción | 0 vulnerabilidades |
| Hashes del lock de generalización | 7/7 coinciden |
| Corpus sintético: manejo seguro no final | 6/6 |
| Corpus sintético: propuestas inseguras | 0 |
| Corpus externo completo: intención | 69/85 |
| Corpus externo completo: campos | 199/290 |
| Corpus externo completo: compuestos detectados | 25/25 |
| Corpus externo completo: violaciones monetarias críticas | 0/67 |
| Replay offline P01_R1 | 25 registros; 0 violaciones críticas |

## Artefactos privados/reproducibles

- `data/runtime/batch-baseline/synthetic-engine-1.1.json`
- `data/runtime/batch-baseline/external-full-engine-1.1.json`
- `data/runtime/batch-baseline/p01-r1-replay-engine-1.1.json`

El replay de R1 no establece ground truth humano: sus 25 registros carecen de outcomes terminales medibles. No se ejecutó replay de P01_R2 porque la ronda no está congelada.

## Estado de producción comprobado en modo lectura

- Git checkout Oracle: `47dabdcf8eaca9ce71fdf164fc7893b691ba92c1`.
- Configuración documentada: Engine `1.1.0`, parser `rules-v0.1.0+explicit-v0.4.0+context-v0.2.0+safety-v0.2.0`, ronda `P01_R2`.
- API y web activas; health local y HTTPS: `status=ok`, `database=ok`.
- No se ejecutaron migraciones, escrituras, reinicios, pulls ni despliegues en Oracle.

## Gate de partida

`BASELINE_1_1_REPRODUCED`. El desarrollo batch debe conservar todas estas regresiones y mantener cero violaciones financieras críticas antes de poder emitir `BATCH_ENGINE_TECHNICAL_GO`.
