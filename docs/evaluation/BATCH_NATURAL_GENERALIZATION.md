# Generalización batch natural — Engine 1.2

**Decisión:** `BATCH_GENERALIZATION_HOLD`

**Evidencia disponible:** desarrollo manual, sintético y web-derived; no existe todavía batch natural independiente ni real.

El corpus `MANUAL_NATURAL_BATCH_DEVELOPMENT` contiene 100 narrativas únicas, 260 operaciones esperadas y 123 campos anotados. Engine 1.2 alcanzó 100% de integridad de spans, cero cruces de monto, cero cruces de cliente y cero violaciones financieras críticas. El detalle reproducible está en [`BATCH_NATURAL_DEVELOPMENT_EVALUATION.md`](BATCH_NATURAL_DEVELOPMENT_EVALUATION.md).

La mejora frente al benchmark web-derived es fuerte en el corpus natural de desarrollo, pero no demuestra generalización: batch exacto fue 76% y recuperación parcial segura 92,31% en el corpus manual, mientras el benchmark web-derived congelado permanece en 13,33% de batch exacto y 30,00% de recall de operaciones. La diferencia de forma y alcance impide combinarlos en una sola métrica.

## Gate

- `BATCH_NATURAL_DEVELOPMENT_EVALUATED`: aprobado.
- `BATCH_GENERALIZATION_GO`: no emitido.
- La API y la UI batch permanecen detrás de banderas apagadas.
- Próximo gate: corpus natural independiente o real, congelado antes de evaluar, con cero cruces de monto/cliente, 100% de spans y cero violaciones críticas.

No se introduce LLM: los errores restantes deben analizarse primero como clases generales de segmentación y alcance. El hold de batch no bloquea la liberación del flujo individual de Engine 1.2.
