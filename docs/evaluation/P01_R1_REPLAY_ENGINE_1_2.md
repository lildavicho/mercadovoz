# Replay de seguridad P01_R1 con Engine 1.2 batch

**Fecha:** 30 de agosto de 2026

## Alcance

El export privado congelado de P01_R1 se leyó localmente con el replay genérico. No se cambió el archivo, no se publicó texto ni se escribió en Oracle.

## Resultado agregado

- registros: 25;
- Engine candidato: `1.2.0`;
- comparaciones: 16 iguales, 1 mejora, 4 mejoras de límite, 3 abstenciones más seguras y 1 cambio sin ground truth;
- violaciones financieras críticas: 0;
- SHA-256 privado: `98c7be160bb3539fbec71e24e1deec026b36a7490bc9e41cd479f57bb8ef99f0`;
- ground truth evaluado: no;
- outcomes humanos: siguen ausentes, por lo que no se calcula accuracy.

Este replay solo demuestra que el sidecar puede procesar el corpus congelado sin romper invariantes estructurales. No convierte `CONFIRMED` en ground truth, no reetiqueta R1 y no autoriza cambios por frase.

P01_R2 se evalúa por separado en [`P01_R2_REPLAY_ENGINE_1_2.md`](P01_R2_REPLAY_ENGINE_1_2.md).
