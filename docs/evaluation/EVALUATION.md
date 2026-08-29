# Evaluación

## Métricas

- **Intent accuracy:** intención correcta entre ejemplos con una intención esperada.
- **Field accuracy:** campos esperados extraídos con el valor correcto; tolerancia numérica de un centavo.
- **Exact operation accuracy:** operaciones `COMPLETE` cuyo estado y todos los campos coinciden.
- **Core exact operation accuracy:** la anterior, restringida a `SALE`, `EXPENSE`, `RECEIVABLE` y `PAYMENT_RECEIVED`.
- **Confirmation recovery:** correcciones que terminan en una operación completa idéntica a la esperada.
- **Abstention precision:** abstenciones correctas entre todas las abstenciones del parser.
- **Abstention recall:** casos que debían abstenerse y efectivamente lo hicieron.

El gate usa `core exact`, no el promedio global. `PURCHASE` y `STOCK_ADJUSTMENT` se reportan, pero son exploratorias. Una operación con campos monetarios no se considera aceptable solo porque la intención sea correcta.

## Resultado reproducible — reglas v0.1

Ejecución del 28 de agosto de 2026 sobre [`evaluation.jsonl`](../../research/benchmarks/synthetic/evaluation.jsonl):

| Métrica | Resultado | Conteo |
|---|---:|---:|
| Intent accuracy | 100% | 29/29 |
| Field accuracy | 100% | 80/80 |
| Exact operation accuracy | 100% | 24/24 |
| Core exact operation accuracy | 100% | 19/19 |
| Confirmation recovery | 100% | 6/6 |
| Abstention precision | 100% | 6/6 predichas |
| Abstention recall | 100% | 6/6 esperadas |

Latencia local observada: media 0,140 ms por frase, mediana y máximo registrados en [`heldout-rules.json`](../../research/benchmarks/results/heldout-rules.json). La cifra varía por máquina y no incluye red, ASR ni interfaz.

## Costo

El motor probado es `deterministic-rules-baseline` v0.1.0: modelo `null`, 0 tokens, USD 0 de API por interpretación y USD 0 por 100 operaciones. Esto excluye dispositivo, hosting, soporte y futura transcripción de voz.

Para cualquier comparador LLM se registrarán tokens reales y tarifas vigentes en la fecha de ejecución. La fórmula será:

```text
costo_operación = tokens_entrada/1 000 000 × tarifa_entrada
                + tokens_salida/1 000 000 × tarifa_salida
costo_100 = costo_operación × 100
```

No se asigna una cifra ficticia a un modelo no ejecutado y todavía no se fija precio mensual.

## Enfoques

| Enfoque | Estado | Ventaja | Riesgo | Decisión Sprint 0 |
|---|---|---|---|---|
| A. Reglas | Ejecutado | auditable, rápido, sin costo API | cobertura frágil ante lenguaje inesperado | baseline actual |
| B. LLM structured output | No ejecutado | mejor variación semántica potencial | costo, latencia, no determinismo y datos | no justificarlo sin corpus real |
| C. Híbrido | Diseñado, no ejecutado | interpretación flexible con totales y schemas deterministas | mayor complejidad | primer comparador si fallan reglas reales |

La intuición híbrida sigue siendo plausible, pero esta prueba no la confirma. El comparador correcto usa exactamente el mismo conjunto real congelado y no permite que el LLM calcule o sobrescriba totales sin validación.

## Interpretación

Los umbrales ≥80% y ≥90% se superan solo en el banco sintético. Debido a que la muestra no proviene de usuarios y fue creada dentro del mismo marco conceptual, la confianza externa es **baja**. El resultado valida el evaluador, el contrato y el flujo de corrección; no valida demanda, acento, vocabulario real ni precisión comercial.

La primera evaluación real seguirá [`REAL_EVALUATION.md`](REAL_EVALUATION.md) y guardará `data/private/real-baseline-v0.json` antes de cualquier regla v2, LLM o híbrido. Se añadirán coverage y unknown language rate sin cambiar las fórmulas sintéticas.

## Medición de seguridad — wrapper v1

El 29 de agosto de 2026 se ejecutó la capa `rules-v0.1.0+context-v0.1.0+safety-v0.1.0`. Las métricas no reemplazan las de v0 y no son accuracy real.

| Corpus | Rol | Manejo no final seguro | Propuestas con operación esperada nula | Compuestos | Contexto seguro |
|---|---|---:|---:|---:|---:|
| sintético held-out | regresión conocida | 6/6 | 0 | n/a | n/a |
| P00-WEB | exploratorio | 18/18 | 0 | 3/3 | n/a |
| P01-WEB-DERIVED | simulación web | 20/20 | 0 | 3/3 | 9/9 |

En el sintético, v1 obtiene 19/24 operaciones completas exactas y 100% de manejo seguro de los seis casos no finales. El descenso desde 24/24 no es una comparación de modelos: cinco etiquetas sintéticas asumían como suficiente lenguaje que ahora se considera ambiguo por precio unitario/total o por alcance personal/comercial. v0 permanece congelado en 24/24.

Los reportes completos están en [`synthetic-engine-v1.json`](../../research/benchmarks/results/synthetic-engine-v1.json), [`p00-web-engine-v1.json`](../../research/benchmarks/results/p00-web-engine-v1.json) y [`p01-web-derived-engine-v1.json`](../../research/benchmarks/results/p01-web-derived-engine-v1.json). El evaluador v1 conserva cada caso, versión, contexto, campos, warnings y latencia.

La mejora de seguridad sobre corpus ya inspeccionados puede estar sobreajustada. Solo un corpus real separado permitirá saber si los bloqueos evitan errores sin volver el flujo inutilizable.

## Benchmark externo `external-cuenca-v1`

Los cuatro archivos entregados se congelaron antes de predecir. Son 240 expresiones `WEB_DERIVED_MULTISOURCE`, no participantes reales. La procedencia, hashes y distribuciones están en [`EXTERNAL_CORPUS_LOCK.md`](EXTERNAL_CORPUS_LOCK.md); la partición y sus límites en [`EXTERNAL_SPLIT_LOCK.md`](EXTERNAL_SPLIT_LOCK.md).

### Primera corrida sin cambios

| Motor | Intent explícito | Campos | Exacta anotada | Contexto seguro | Compuestos | Violaciones monetarias |
|---|---:|---:|---:|---:|---:|---:|
| v0 congelado | 33/85 | 77/290 | 17/85 | 60/60 | 3/25 | 17/67 |
| v1 inicial | 33/85 | 77/290 | 17/85 | 60/60 | 25/25 | 0/67 |

v1 mejoró seguridad sin mejorar todavía cobertura explícita. Los 17 fallos monetarios v0 fueron: tres compuestos finalizados como una operación, ocho sumas falsas por coordinación y seis retiros personales clasificados como stock.

### Iteraciones generales

Solo development limpio orientó cambios; no se inspeccionaron predicciones caso por caso del held-out.

| Corte | Intent explícito | Campos | Exacta anotada | Violaciones monetarias |
|---|---:|---:|---:|---:|
| Development limpio, iteración 1 | 42/45 | 127/142 | 39/45 | 0/48 |
| Development limpio, iteración 2 | 45/45 | 136/142 | 39/45 | 0/48 |
| Held-out independiente limpio, cierre | 11/11 | 40/44 | 7/11 | 0/4 |
| Corpus completo, cierre | 69/85 | 199/290 | 49/85 | 0/67 |

La iteración 1 añadió patrones generales de ventas explícitas y gastos logísticos. La iteración 2 reconoce `salieron ... a N` pero pide confirmación cuando `N` no declara si es precio unitario o total. Esa abstención explica cuatro desacuerdos de exactitud anotada en held-out y es preferida por seguridad.

### Anti-leakage y calidad

- 75/240 casos comparten skeleton con P00/P01-WEB; 22 estaban en held-out y se excluyeron del conjunto independiente.
- 42/240 contienen artefactos como `unidads` o `pars`; siete estaban en held-out independiente y se excluyeron del corte limpio.
- El held-out independiente limpio contiene 29 registros y cobertura parcial. No soporta una promesa de accuracy general.

**Resultado:** `TECHNICAL_GO` para el core y Text MVP local; `FIELD_VALIDATION_STATUS = PENDING_REAL_DATA`. Reportes reproducibles: [`external-cuenca-v1-baseline-v0.json`](../../research/benchmarks/results/external-cuenca-v1-baseline-v0.json), [`external-cuenca-v1-engine-v1-sprint1-exit.json`](../../research/benchmarks/results/external-cuenca-v1-engine-v1-sprint1-exit.json) y [`external-heldout-v1-independent-clean-engine-v1-sprint1-exit.json`](../../research/benchmarks/results/external-heldout-v1-independent-clean-engine-v1-sprint1-exit.json).
