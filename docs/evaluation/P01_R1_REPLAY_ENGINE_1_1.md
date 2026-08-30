# Replay de P01_R1 con Engine 1.1

**Fuente:** export privado congelado de `P01_R1`  
**Origen histórico:** Engine `1.0.0`  
**Motor de replay:** Engine `1.1.0`  
**Registros:** 25  
**Rol:** análisis técnico de `REAL_DEVELOPMENT`, no nueva captura

## Resultado

| Clasificación comparativa | Conteo |
|---|---:|
| Resultado equivalente | 17 |
| Mejora de límite técnico conocido | 4 |
| Abstención más segura | 2 |
| Pronombre eliminado como cliente | 1 |
| Cambio sin ground truth | 1 |

Violaciones financieras críticas detectadas por el replay: **0**.

Entre los ocho cambios, dos propuestas parciales de venta pasan a estado compuesto sin operación; cuatro aplican límites generalizados de producto/precio; un pago deja de usar un pronombre como cliente y solicita contexto; y un pago con cliente nombrado pasa a completo, aunque no puede llamarse mejora sin ground truth humano.

## Gate de regresión

`NO_CRITICAL_REGRESSION_PASS`. El resultado permite considerar Engine 1.1 para una ronda nueva, pero no reinterpreta ni sobrescribe la evidencia histórica de R1. El archivo de replay privado conserva la salida por registro y tiene SHA-256 `338d9758c00261bd15a2e8032834d3d7d362153ed033e8b23f7afc4e9e83b028`.

## Separación obligatoria

- Las predicciones históricas de R1 permanecen asociadas a Engine 1.0.
- Las salidas de replay no son `P01_R2`, outcomes humanos ni etiquetas gold.
- Ninguna métrica de ambos motores se suma en una “accuracy total”.
- Cualquier comparación posterior debe declarar motor, ronda, población y denominador.
