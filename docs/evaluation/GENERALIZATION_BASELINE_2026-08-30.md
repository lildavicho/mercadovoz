# Baseline previo al hardening de generalización

**Fecha:** 30 de agosto de 2026  
**Commit base:** `d83955d`  
**Engine:** `1.0.0`  
**Evidencia nueva:** `MANUAL_REGRESSION_DEVELOPMENT`; no es `REAL_HELDOUT` ni evidencia de validación de mercado.

## Reproducción manual

Los cinco casos reportados se reprodujeron antes de modificar el motor:

| Familia | Resultado previo |
|---|---|
| límite producto/precio | producto contaminado; faltan `unit_price` y `total` |
| centavos | producto contaminado; no se normaliza `0.50` |
| total explícito | producto contaminado; no se conserva `total` |
| pronombre como cliente | `customer = Me`; resultado incorrectamente `COMPLETE` |
| venta compuesta repetida | segunda venta absorbida por el producto de la primera |

La suite dedicada contiene cinco pruebas y falla `5/5` por esas causas antes del cambio.

## Métricas históricas reproducidas

### Externo independiente limpio

- intención explícita: `11/11`;
- campos disponibles: `40/44` (`90.91%`);
- operación exacta anotada: `7/11` (`63.64%`);
- compuestos: `3/3`;
- manejo seguro de contexto: `7/7`;
- violaciones financieras críticas: `0/4`;
- abstención fuera de alcance: `2/2`.

### Corpus externo completo

- intención: `69/85` (`81.18%`);
- campos: `199/290` (`68.62%`);
- operación exacta: `49/85` (`57.65%`);
- compuestos: `25/25`;
- violaciones financieras críticas: `0/67`;
- abstención fuera de alcance: `21/21`.

### Sintético de evaluación

- coincidencia de estado: `22/30` (`73.33%`);
- intención: `22/29` (`75.86%`);
- campos esperados: `58/80` (`72.50%`);
- manejo no final seguro: `6/6`;
- propuestas inseguras: `0`.

Los resultados se guardaron en `data/runtime/`, fuera de Git. Los reportes históricos versionados no se modifican.
