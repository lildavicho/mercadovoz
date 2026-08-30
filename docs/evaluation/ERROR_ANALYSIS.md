# Análisis de errores

## Resultado actual

El reporte retenido no contiene discrepancias: 0 errores en 30 ejemplos. No debe interpretarse como ausencia de riesgo. Es una señal de que el banco sintético es demasiado cercano al dominio conocido para discriminar entre reglas, LLM e híbrido.

El evaluador ya clasifica discrepancias como:

- `intent_incorrect`;
- `number_incorrect`;
- `unit_incorrect`;
- `product_omitted` / `product_incorrect`;
- `total_incorrect`;
- `person_incorrect`;
- `abstention_incorrect`;
- `local_expression_not_understood`;
- `hallucination`;
- `compound_operation`.

También produce categorías específicas para cualquier otro campo omitido o incorrecto. Los reportes públicos históricos están en `research/benchmarks/results/*.json`; una evaluación real queda en `data/private/`, con texto, esperado, predicho y categorías por caso.

## Riesgos no probados

1. Variación léxica y sintáctica real de Cuenca, muletillas, autocorrecciones y frases incompletas.
2. Palabras numéricas fuera del rango simple, precios decimales dichos de distintas maneras y promociones.
3. Productos con nombres compuestos, apodos locales y unidades no listadas.
4. Contrapartes de varias palabras, homónimos y frases donde “pagué” significa gasto o abono.
5. Operaciones compuestas y deudas por pagar; `PAYABLE` no está en el esquema actual.
6. Errores de ASR por ruido, acento, nombres, números y unidades.

## Protocolo de mejora

Después de obtener corpus real, ordenar categorías por frecuencia y severidad monetaria. Corregir primero alucinaciones, números/totales y abstenciones incorrectas; después intención y campos descriptivos. Cada cambio se hace solo con desarrollo. El conjunto retenido se ejecuta al cerrar una versión, no frase por frase.

Si una categoría representa más de 30% de los fallos, reducir temporalmente esa intención o vocabulario y repetir el gate. No añadir una regla para una frase individual sin al menos dos ejemplos de variación que demuestren el patrón.

## Comparación real pendiente

`data/private/real-baseline-v0.json` deberá conservar la comparación contra el 100% sintético, aunque exista una caída grande. Antes de proponer soluciones, clasificar `UNKNOWN_UNIT`, `UNKNOWN_EXPRESSION`, `IMPLICIT_AMOUNT`, `COMPOUND_OPERATION`, `OUT_OF_SCOPE_INTENT`, `AMBIGUOUS_REFERENCE`, `UNEXPECTED_STRUCTURE`, `ABBREVIATION` y `OTHER`. La ausencia actual de casos reales no se registra como cero errores reales.

El [análisis P00-WEB](P00_WEB_ANALYSIS.md) es exploratorio y adversarial. Sus 25 casos no se mezclan con esta comparación real ni sustituyen P01+.

El [análisis P01-WEB-DERIVED](P01_WEB_DERIVED_ANALYSIS.md) es una simulación de campo no elegible para held-out. Sus categorías de contexto y seguridad son hipótesis para entrevistas, no frecuencias de usuarios.

## Regresiones de seguridad v1

Los siguientes fallos observados en los corpus exploratorios tienen pruebas permanentes en `tests/test_safety_v1.py`:

| Fallo | Resultado v0 observado | Conducta v1 |
|---|---|---|
| `cinco y una` | cantidad `6` dentro de una venta parcial | `COMPOUND_OPERATION`, sin propuesta |
| ingreso + gasto | gasto `COMPLETE`, ingreso omitido | `COMPOUND_OPERATION`, sin propuesta |
| retiro para la casa | ajuste de stock parcial | `OUT_OF_SCOPE`, sin propuesta |
| deuda existente | riesgo de tratar estado como evento | `NEEDS_CONTEXT`, sin deuda nueva |
| valor aproximado | riesgo de exactitud falsa | `AMBIGUOUS`, sin importe exacto |
| precio sin “cada/total” | asunción de base del precio | `AMBIGUOUS`, sin cálculo |
| comida personal/negocio | gasto completo sin alcance | `AMBIGUOUS`, sin propuesta |

Esto demuestra comportamiento ante esas frases, no cobertura de todas sus variantes. No se añadió vocabulario general a v0 y ninguna corrección modifica los resultados históricos.

## Hallazgos del corpus externo

La primera corrida v0 expuso 17 violaciones monetarias críticas entre 67 casos de riesgo: compuestos reducidos a una operación, coordinación numérica sumada falsamente y retiros personales interpretados como stock. La barrera v1 eliminó esas violaciones antes de añadir cobertura.

Dos iteraciones generales se justificaron con development:

1. variantes explícitas limpias de venta y gastos de logística;
2. patrón `salieron ... a N`, conservando `NEEDS_CONFIRMATION` cuando la base del precio es ambigua.

No se creó una regla para aceptar los 42 plurales artificiales `unidads`/`pars`. Esos registros se conservan como riesgo de calidad y se reportan en el resultado completo. Tampoco se usaron los 22 held-out con fuga estructural para afirmar generalización.

El cierre independiente limpio conserva cuatro desacuerdos exactos por una decisión de seguridad: la etiqueta aporta un precio interpretable, pero el texto no explicita si es unitario o total. La intención y los campos no ambiguos se extraen; la operación no se presenta como completa.

Vacíos pendientes: lenguaje espontáneo, autocorrecciones humanas, ruido de voz, tiempo de tarea, comprensión de la boleta, tasa de confirmación equivocada y preferencia frente al método actual. Todos requieren campo real.

## Hardening de generalización 1.1.0

Los cinco fallos manuales del 30 de agosto se registraron como `MANUAL_REGRESSION_DEVELOPMENT`. La taxonomía permanente incluye ahora `SALE_PRODUCT_BOUNDARY_ERROR`, `SALE_PRICE_EXTRACTION_ERROR`, `CENTAVOS_NORMALIZATION_ERROR`, `TOTAL_VS_UNIT_PRICE_ERROR`, `PRONOUN_AS_CUSTOMER_ERROR`, `COMPOUND_OPERATION_NOT_DETECTED`, `COMPOUND_OPERATION_COLLAPSED`, `EXISTING_DEBT_DUPLICATION`, `APPROXIMATION_TO_EXACT_AMOUNT`, `PERSONAL_WITHDRAWAL_MISCLASSIFIED`, `CONTEXT_FALSE_RESOLUTION`, `NUMERIC_COORDINATION_ERROR`, `UNSAFE_AUTO_COMPLETION`, `CORRECTION_FAILURE` y `CONTEXT_EXPIRY_ERROR`.

La primera propuesta amplia fue rechazada al reducir el held-out limpio de 40/44 a 33/44 campos: el punto decimal se había tratado como separador de operaciones. Tras minimizar esa causa, el benchmark recuperó exactamente sus métricas previas y mantuvo 0 violaciones críticas. Esta iteración fallida queda documentada para evitar reintroducir detección de compuestos basada en puntuación sin distinguir decimales.
