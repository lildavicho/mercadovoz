# Replay de seguridad P01_R1 con Engine 1.2 batch

**Fecha:** 30 de agosto de 2026

## Alcance

El export privado congelado de P01_R1 se leyó localmente mediante `scripts/evaluation/replay_real_batch_safety.py`. No se cambió el archivo, no se publicó texto, no se escribió en Oracle y no se utilizó P01_R2.

## Resultado agregado

- registros: 25;
- Engine candidato: `1.2.0`, `input_mode=TEXT_SINGLE`;
- fallos de source span: 0;
- operaciones confirmables con tipo/monto inválido: 0;
- estados: 9 `READY`, 4 `PARTIALLY_READY`, 10 `NEEDS_REVIEW`, 2 `BLOCKED`;
- ground truth evaluado: no;
- outcomes humanos: siguen ausentes, por lo que no se calcula accuracy.

Este replay solo demuestra que el sidecar puede procesar el corpus congelado sin romper invariantes estructurales. No convierte `CONFIRMED` en ground truth, no reetiqueta R1 y no autoriza cambios por frase.

## P01_R2

No se ejecutó replay: la ronda no está congelada. Su evidencia permanece fuera del desarrollo hasta cierre y lock explícitos.
