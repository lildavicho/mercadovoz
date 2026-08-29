# P01-WEB-DERIVED — análisis baseline v0

## Procedencia y límites

Las 25 entradas son una simulación de campo derivada de evidencia pública; no son declaraciones del usuario ni transcripciones de una entrevista. El corpus registra `source_type=WEB_DERIVED_FIELD_SIMULATION`, `real_interview=false`, `eligible_for_final_heldout=false` y `real_participant=false` en cada línea.

Puede orientar development, schema, contexto y confirmaciones. No es accuracy real, validación comercial, held-out independiente ni autorización de Sprint 1. P01 real continúa reservado y pendiente.

## Reproducibilidad

Antes de ejecutar el parser el 29 de agosto de 2026 se comprobaron los ocho hashes del baseline: **PASS 8/8**.

```text
81828310512a349597496587fb1fee36de79246fa69fb850881779f4d3304cce  research/benchmarks/web-derived/P01_WEB_DERIVED_CORPUS.jsonl
6494540e521cdb1af806f90ba7bf8f4c3c48ab4deaaaff52c3d8713ba3d9bfee  research/benchmarks/results/p01-web-derived-baseline-v0.json
```

```powershell
python scripts\evaluation\evaluate_real_corpus.py research\benchmarks\web-derived\P01_WEB_DERIVED_CORPUS.jsonl --exploratory-corpus P01-WEB-DERIVED --output data\runtime\p01-web-check.json
```

## Métricas descriptivas

| Métrica | Resultado | Conteo |
|---|---:|---:|
| Intent accuracy | 70,6% | 12/17 |
| Field accuracy | 27,8% | 10/36 |
| Exact operation accuracy | 20% | 1/5 |
| Core exact accuracy | 0% | 0/4 |
| Abstention precision | 86,4% | 19/22 abstenciones predichas |
| Abstention recall | 95% | 19/20 abstenciones esperadas |
| Recognition coverage | 60% | 15/25 |
| Complete coverage | 12% | 3/25 |
| Unknown language rate | 88% | 22/25 etiquetadas |

Confirmation recovery es `null`: no hay correcciones conversacionales. Solo `018` fue una operación completa exacta. El 0% core no es estimación de campo porque el corpus fue construido para adversarialidad.

## Separación solicitada

### UNDERSTOOD

- `008`: detectó pago con cliente e importe implícitos y pidió ambos.
- `014`: dejó fuera el aporte personal no modelado.
- `018`: ajuste de stock completo y exacto.
- `020`: no convirtió una deuda existente en una operación nueva.
- `022`: dejó fuera el cierre aproximado.
- `023`: no fabricó el límite “ni veinte” como monto exacto.

### NEEDS_CONFIRMATION_CORRECT

- `008` es el caso limpio: intención correcta, campos implícitos sin inventar y pregunta de confirmación.
- `001`, `009`, `010`, `015`, `016`, `017` y `019` también terminaron en `NEEDS_CONFIRMATION`, pero contienen extracción omitida o incorrecta; se contabilizan en `WRONG_PARSE`, no como éxito pleno.

### WRONG_PARSE

- `001`: incorporó “en 2” al producto en vez de representar la ambigüedad total/unitario.
- `002`–`004`: no reconoció expresiones de venta como “se fueron”, “me llevó” y “salieron”.
- `005` y `007`: el placeholder `[NOMBRE]` rompe extracción de cliente y, en el abono, también del importe. Es artefacto de evaluación; no justifica enseñar corchetes al producto.
- `009`–`010`: identifica pago pero no calcula/extracta el importe contextual.
- `011`: entiende monto pero devuelve `pasajes`, mientras el gold exige la categoría canónica `transporte`; revela ausencia de taxonomía, no necesariamente incomprensión.
- `012`: no reconoce el gasto logístico con “pagué… por”.
- `015`: convierte “en 22” en producto y pierde precio/total.
- `016`: trata “todo eso en el mayorista” como nombre de producto.
- `017`: detecta stock pero pierde cantidad, unidad y modo porque la extracción exige también producto.
- `019`: trata “todo lo que quedaba” como producto literal.
- `021`: no reconoce liquidación de deuda mediante “ya pagó”.

### UNSAFE_INFERENCE

- `013`: “saqué cinco para la casa” se interpreta como `STOCK_ADJUSTMENT`. No queda `COMPLETE`, pero presenta una intención equivocada.
- `024`: “me entraron treinta y gasté ocho…” se guarda conceptualmente como gasto `COMPLETE` de USD 8, perdiendo el ingreso y sin advertir operación compuesta. Es el fallo de seguridad principal.
- `025`: `cinco y una` se normaliza a `6`; propone venta de seis y producto “quedó fiada”. Aunque pide confirmación, corrompe cantidad y semántica.

### SCHEMA_GAP

- Retiro y aporte personal: `013`, `014`.
- Balance anterior/saldo posterior de deuda: `009`.
- Estado versus evento de deuda: `020`.
- Cierre aproximado/no exacto: `022`, `023`.
- Varias operaciones: `006`, `024`, `025`.
- Taxonomía de categorías (`pasajes` → `transporte`): `011`.

Son hipótesis de schema; no se añaden tipos todavía.

### CONTEXT_REQUIRED

`002`, `003`, `007`–`010`, `015`–`017`, `019`–`021` requieren al menos uno de: producto activo, cliente activo, deuda activa, saldo, stock previo o referencia temporal. Son 12/25 casos si se incluyen las referencias implícitas explícitamente marcadas.

El contexto debe ser acotado y verificable: una operación pendiente, cliente seleccionado, deuda activa o producto activo. No se propone memoria conversacional abierta.

### COMPOUND_OPERATION

`006`, `024` y `025` contienen dos eventos. Ninguno recibió `compound_operation_out_of_scope`:

- `006` quedó `UNRECOGNIZED`, seguro pero sin guía para separar.
- `024` quedó `COMPLETE` como un solo gasto, inseguro.
- `025` quedó como venta parcial y además activó el bug numérico.

## Clasificación por caso

| ID | Clasificación primaria | Resultado resumido |
|---|---|---|
| 001 | WRONG_PARSE | status seguro; producto contaminado con “en 2” |
| 002 | CONTEXT_REQUIRED / WRONG_PARSE | venta implícita no reconocida |
| 003 | CONTEXT_REQUIRED / WRONG_PARSE | venta implícita no reconocida |
| 004 | WRONG_PARSE | venta incompleta no reconocida |
| 005 | WRONG_PARSE | cuenta por cobrar sin cliente por placeholder |
| 006 | COMPOUND_OPERATION | abstiene sin identificar componentes |
| 007 | CONTEXT_REQUIRED / WRONG_PARSE | pago detectado; cliente e importe omitidos |
| 008 | NEEDS_CONFIRMATION_CORRECT | pago contextual sin inventar datos |
| 009 | CONTEXT_REQUIRED / WRONG_PARSE | pago detectado; no extrae abono USD 10 |
| 010 | CONTEXT_REQUIRED / WRONG_PARSE | pago detectado; no calcula mitad de USD 30 |
| 011 | SCHEMA_GAP / WRONG_PARSE | categoría literal versus canónica |
| 012 | WRONG_PARSE | gasto logístico no reconocido |
| 013 | UNSAFE_INFERENCE / SCHEMA_GAP | retiro personal confundido con stock |
| 014 | UNDERSTOOD / SCHEMA_GAP | aporte personal correctamente fuera de scope |
| 015 | CONTEXT_REQUIRED / WRONG_PARSE | compra detectada; producto/precio mal separados |
| 016 | CONTEXT_REQUIRED / WRONG_PARSE | referencia “todo eso” tratada como producto |
| 017 | CONTEXT_REQUIRED / WRONG_PARSE | stock detectado; pierde campos explícitos |
| 018 | UNDERSTOOD | operación completa exacta |
| 019 | CONTEXT_REQUIRED / WRONG_PARSE | referencia a stock tratada como producto |
| 020 | UNDERSTOOD / STATE_VS_EVENT | no duplica deuda existente |
| 021 | CONTEXT_REQUIRED / WRONG_PARSE | liquidación contextual no reconocida |
| 022 | UNDERSTOOD / SCHEMA_GAP | aproximación no convertida en venta |
| 023 | UNDERSTOOD | cantidad no exacta no fabricada |
| 024 | UNSAFE_INFERENCE / COMPOUND_OPERATION | pierde ingreso y completa solo gasto |
| 025 | UNSAFE_INFERENCE / COMPOUND_OPERATION | `cinco y una → 6` |

## Implicación técnica

El baseline es razonablemente conservador: 95% de recall de abstención. Sin embargo, la seguridad no puede depender solo de campos obligatorios. Una operación puede estar “completa” y aun omitir otro evento (`024`) o resolver incorrectamente una polisemia (`013`). Se necesitan detectores previos de multioperación, coordinación numérica y contexto financiero, además de confirmación legible.

Agregar expresiones una por una no resolvería producto/cliente/deuda activos. Un LLM tampoco debe introducirse antes de contar con frases independientes y pruebas de no invención.

## Decisión

**CONTINUE + CONTEXT_LAYER_REQUIRED.**

Mantener el baseline v0 congelado hasta ejecutar P01 real. No crear Rules V1, no cambiar schema y no introducir LLM con este corpus. En P01 se debe observar si se repiten: referencias activas, `en` como total/precio, “saqué” monetario, pagos vinculados a deuda y coordinación `cinco y una`. Si se corroboran, priorizar una capa de contexto controlado y un preclasificador de seguridad antes que ampliar regex.
