# Congelamiento — external-cuenca-v1

**Fecha:** 29 de agosto de 2026  
**Dataset version:** `external-cuenca-v1`  
**Rol:** benchmark técnico externo derivado de fuentes públicas  
**Evidencia humana real:** no  
**Elegible para real held-out:** no

## Integridad previa a predicciones

Los cuatro archivos se copiaron sin transformación a [`research/external-cuenca-v1/`](../../research/external-cuenca-v1/). La verificación se realizó antes de ejecutar v0 o v1.

```text
02558a7450035b712c95eb240016efc716a47c3fc66feb57ee62a68ea8bd2788  mercadovoz_cuenca_external_corpus_v1.jsonl
7677bdf464d4615af6ded6e63ac1d2f584cf4931123d84b86ffc58279d61e2d1  mercadovoz_cuenca_external_corpus_v1.csv
2b7163a61de34fe5642c2d6c1c93a9360bba4aebad149ae8936e7e034703b248  mercadovoz_cuenca_sources.csv
fda64af165f26529063fd87fed43e2b919f994d5a9178ff6509ba3a4c283649f  MERCADOVOZ_CUENCA_EXTERNAL_CORPUS_README.md
```

## Validación estructural

- JSONL: 240 líneas válidas, 240 IDs únicos, sin texto ni etiquetas obligatorias vacías.
- CSV: 240 filas y equivalencia semántica 240/240 con el JSONL en ID, texto, fuente, operación, fenómeno, expectativa y gold parcial.
- Fuentes: 14 entradas en el ledger; los 10 `source_id` usados por el corpus existen en ese ledger.
- Locale: 240/240 `es-EC`.
- Procedencia: 240/240 `WEB_DERIVED_MULTISOURCE`.
- `real_participant=false`: 240/240.
- `eligible_for_real_heldout=false`: 240/240.

Los registros no incluyen una propiedad `dataset_version`; la versión se registra en este manifest y en resultados, sin alterar los archivos. El nombre de procedencia es `provenance_type`, no `source_type`.

## Distribución por expected_operation

| Valor | Casos |
|---|---:|
| `SALE` | 100 |
| `NONE` | 43 |
| `EXPENSE` | 19 |
| `PAYMENT_RECEIVED` | 22 |
| `RECEIVABLE` | 6 |
| `STOCK_ADJUSTMENT` | 25 |
| `COMPOUND_OPERATION` | 25 |

## Distribución por phenomenon

| Fenómeno | Casos |
|---|---:|
| `APPROXIMATE_DAILY_CLOSE` | 15 |
| `ARITHMETIC_DEBT_REFERENCE` | 4 |
| `BUSINESS_EXPENSE` | 10 |
| `COMPOUND_INCOME_EXPENSE` | 3 |
| `COMPOUND_PAYMENT_PURCHASE` | 8 |
| `COMPOUND_SALE_PARTIAL_PAYMENT` | 3 |
| `COMPOUND_SALE_RECEIVABLE_NUMERIC_COORDINATION` | 3 |
| `EXPLICIT_QUANTITY_UNIT_PRICE` | 60 |
| `EXPLICIT_STOCK` | 11 |
| `IMPLICIT_CUSTOMER_AMOUNT_TEMPORAL` | 10 |
| `IMPLICIT_PRODUCT` | 13 |
| `IMPLICIT_PRODUCT_AND_TOTAL` | 10 |
| `IMPLICIT_QUANTITY_FROM_STOCK` | 15 |
| `LOGISTICS_EXPENSE` | 9 |
| `NEW_RECEIVABLE` | 6 |
| `NUMERIC_COORDINATION_CINCO_Y_UNA` | 8 |
| `OWNER_CONTRIBUTION_SCHEMA_GAP` | 5 |
| `OWNER_WITHDRAWAL_SCHEMA_GAP` | 6 |
| `PARTIAL_PAYMENT` | 8 |
| `PRICE_TOTAL_AMBIGUITY` | 9 |
| `PROMOTION_NEGOTIATION` | 10 |
| `STATE_VS_EVENT` | 7 |
| `ZERO_STOCK` | 7 |

## Distribución por source_id

| Fuente | Casos |
|---|---:|
| `CUENCA_ITB_VISA_CENTER` | 32 |
| `CUENCA_KILLKANA_ARENAL_2021` | 33 |
| `CUENCA_MUNICIPIO_10AGOSTO_2023` | 12 |
| `CUENCA_MUNICIPIO_CUSNI_2025` | 37 |
| `CUENCA_PRIMICIAS_CASERITA_2025` | 12 |
| `CUENCA_SCIELO_SININCAY_2023` | 32 |
| `CUENCA_UCUENCA_12ABRIL_2024` | 5 |
| `CUENCA_UCUENCA_LEXICON_2013` | 26 |
| `ECUADOR_UNL_RECEIVABLES` | 17 |
| `ECUADOR_YAPPA_TESTIMONIALS` | 34 |

El ledger contiene cuatro fuentes adicionales no asignadas a registros. Su presencia no se interpreta como evidencia adicional por caso.

## Distribución por safety_expectation

| Expectativa | Casos |
|---|---:|
| `PROPOSE_OR_CONFIRM` | 103 |
| `NEEDS_CONTEXT` | 60 |
| `DETECT_COMPOUND_AND_SPLIT_OR_CONFIRM` | 25 |
| `DO_NOT_CREATE_EXACT_FINANCIAL_OPERATION` | 15 |
| `OUT_OF_SCOPE_OR_CONFIRM` | 11 |
| `OUT_OF_CORE_OR_CONFIRM` | 10 |
| `NEEDS_CONFIRMATION` | 9 |
| `NO_NEW_OPERATION` | 7 |

## Regla de congelamiento

El JSONL y sus archivos acompañantes no se editarán para mejorar métricas. La partición, subsets y etiquetas derivadas vivirán en manifests nuevos referidos por ID. Cualquier cambio crea una versión nueva y conserva esta v1. Antes de toda reevaluación se verificará el hash del JSONL.
