# ADR-006 — Orquestador batch lateral al Engine 1.1 congelado

## Contexto

P01_R2 evalúa Engine 1.1.0. La narrativa multioperación exige nuevos contratos, pero editar los módulos bloqueados contaminaría la ronda y rompería la trazabilidad histórica.

## Opciones

1. modificar el parser 1.1 en el lugar;
2. duplicar todo el motor y evolucionar la copia;
3. añadir un orquestador versionado que componga Engine 1.1 por segmento y contenga únicamente la semántica batch nueva.

## Decisión

Se elige la opción 3. Engine 1.2.0 será aditivo: segmentador, modelos, workflow y validadores batch viven en un módulo separado. Los hashes de Engine 1.1 permanecen intactos. El servicio y SQLite reciben extensiones detrás de un feature flag, sin cambiar los endpoints simples.

## Razón

La composición conserva regresiones, permite comparar 1.1 frente a 1.2 y mantiene un rollback claro. La duplicación completa crearía dos fuentes de verdad; editar 1.1 violaría el lock de la ronda.

## Trade-offs

- Existe una capa de adaptación entre schemas individual y batch.
- Algunas mejoras de una operación solo estarán disponibles al usar el endpoint batch hasta una futura release.
- Las propuestas continúan en memoria en esta fase; la confirmación sí es durable e idempotente.

## Reversibilidad

Alta. El flag puede deshabilitar endpoints batch y la migración es forward-only/aditiva. No se reescriben filas históricas.

## Evidencia

Baseline documentado en [`BATCH_ENGINE_BASELINE.md`](../evaluation/BATCH_ENGINE_BASELINE.md) y hashes 7/7 del lock 1.1.
