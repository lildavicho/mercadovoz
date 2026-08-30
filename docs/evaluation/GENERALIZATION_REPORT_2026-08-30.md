# Evaluación de generalización — engine 1.1.0

**Evidencia:** desarrollo técnico; no es validación de campo.  
**Fuente manual:** `MANUAL_REGRESSION_DEVELOPMENT`; nunca `REAL_HELDOUT`.

## Causas raíz y solución

| Clase | Causa raíz | Cambio general |
|---|---|---|
| `SALE_PRODUCT_BOUNDARY_ERROR` | el parser legado consumía el sufijo monetario como producto | gramática previa al parser congelado que separa cuerpo, base de precio y monto |
| `CENTAVOS_NORMALIZATION_ERROR` | la regla explícita solo aceptaba dólares numéricos | normalización monetaria con `Decimal` para centavos, coma/punto y USD explícito |
| `TOTAL_VS_UNIT_PRICE_ERROR` | no existía representación segura de total declarado sin precio unitario | conservar `total`, omitir `unit_price` y mantener `NEEDS_CONFIRMATION` |
| `PRONOUN_AS_CUSTOMER_ERROR` | el primer token podía convertirse en contraparte | lista gramatical de pronombres prohibidos y contexto requerido |
| `COMPOUND_OPERATION_COLLAPSED` | la detección contaba categorías, no predicados repetidos | conteo de predicados y conectores; multi-producto se abstiene mientras no haya line items |
| `UNSAFE_AUTO_COMPLETION` | la confirmación validaba forma, no estado de interpretación | confirmación permitida solo desde `COMPLETE` |

No se añadieron reglas por producto ni por frase. El parser histórico, el normalizador numérico y los reportes históricos permanecen sin reescritura.

## Comparación reproducida

| Dataset separado | Métrica | Antes | Engine 1.1.0 |
|---|---|---:|---:|
| externo limpio | intención | 11/11 | 11/11 |
| externo limpio | campos | 40/44 | 40/44 |
| externo limpio | exacta anotada | 7/11 | 7/11 |
| externo limpio | compuestos | 3/3 | 3/3 |
| externo limpio | violaciones críticas | 0/4 | 0/4 |
| externo completo | intención | 69/85 | 69/85 |
| externo completo | campos | 199/290 | 199/290 |
| externo completo | exacta anotada | 49/85 | 49/85 |
| externo completo | compuestos | 25/25 | 25/25 |
| externo completo | violaciones críticas | 0/67 | 0/67 |
| sintético evaluación | estado | 22/30 | 22/30 |
| sintético evaluación | campos | 58/80 | 58/80 |
| sintético evaluación | propuesta insegura | 0 | 0 |

Las cinco regresiones manuales pasan `5/5`. La matriz determinista recorre 3.600 combinaciones de verbos, cantidades, unidades, productos, precios y bases; verifica ausencia de crashes, números finitos/positivos, aritmética consistente y prohibición de pronombres como cliente. Ese volumen es prueba sintética de invariantes, no precisión humana.

## Política monetaria

- Ecuador/piloto opera en USD solo cuando la cláusula monetaria o el flujo aprobado lo establece.
- `cada`, `por unidad`, `la libra` y `precio unitario` habilitan `unit_price` y cálculo `quantity × unit_price` con `Decimal`.
- `en total`, `total` o `por todo` conserva el total declarado y no invierte automáticamente la división.
- Una base no distinguible termina en `AMBIGUOUS` o `NEEDS_CONFIRMATION`.
- Una corrección de total inconsistente no puede confirmarse hasta resolver la inconsistencia.

## Límites pendientes

- No hay line items: ventas multi-producto se abstienen.
- No se soporta toda permutación del orden de palabras; entradas desconocidas deben quedar no finales.
- El vocabulario sintético malformado (`unidads`, `pars`) no se incorpora como español válido.
- No existe métrica de recuperación de corrección humana real; solo pruebas automatizadas.
- No hay `REAL_HELDOUT`, outcomes terminales suficientes, HTTPS ni cierre de P01 Round 1.

**Gate técnico:** `TECHNICAL_GENERALIZATION_GO`.  
**Gate de campo:** `HOLD_REAL_FIELD_DATA_REQUIRED`.
