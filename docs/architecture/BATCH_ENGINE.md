# Diseño del motor batch 1.2

**Estado:** `BATCH_ENGINE_TECHNICAL_GO / BATCH_GENERALIZATION_HOLD`

**Versión candidata:** Engine `1.2.0`, schema `batch-operation-v1`

**Producción:** código integrado, rutas y UI desactivadas por bandera

## Problema y límite

Engine 1.2 conserva el contrato `texto → interpretación individual` y agrega un orquestador lateral. Segmenta una narración, llama al mismo core 1.2 para cada fragmento y aplica validadores batch explícitos antes de permitir confirmación. No existe un segundo parser financiero.

```text
source text
  → CommercialNarrativeSegmenter
  → ordered source spans
  → Engine 1.2 single-operation core per span
  → batch-only structured adapters
  → relationships and dependencies
  → BatchProposal
  → human review
  → transactional persistence
```

## Contrato

```text
BatchInterpretation
  batch_id
  source_text
  input_mode: TEXT_SINGLE | TEXT_BATCH | VOICE_TRANSCRIPT
  engine_version: 1.2.0
  underlying_engine_version: 1.2.0
  segments: SegmentInterpretation[]
  groups: TransactionGroup[]
  warnings: string[]
  status: READY | PARTIALLY_READY | NEEDS_REVIEW | BLOCKED

SegmentInterpretation
  segment_id
  sequence
  source_span: {start, end}
  source_text
  state
  operation | null
  fields_extracted
  computed_fields
  field_provenance
  context_used
  warnings
  depends_on: segment_id[]
  confirmable

TransactionGroup
  group_id
  type
  customer
  related_segment_ids
  item_ids
  derived_relationships
```

Los offsets son índices de caracteres Unicode con intervalo semiabierto `[start, end)`. `source_text[start:end]` debe ser exactamente el texto guardado en el segmento.

## Estados y éxito parcial

- `READY`: todos los ítems son confirmables.
- `PARTIALLY_READY`: existe al menos un ítem confirmable y al menos uno bloqueado para revisión.
- `NEEDS_REVIEW`: ningún ítem es confirmable, pero hay contexto/corrección posible.
- `BLOCKED`: no existe movimiento financiero que pueda proponerse con seguridad.

Solo `COMPLETE` es confirmable. `NEEDS_CONFIRMATION`, `NEEDS_CONTEXT`, `AMBIGUOUS`, `OUT_OF_SCOPE`, `UNSAFE`, `UNRECOGNIZED` y un compuesto residual permanecen bloqueados. El frontend no es autoridad: el backend vuelve a validar el estado.

## Segmentación determinista

La segmentación usa un escáner de cláusulas, no una colección de reemplazos por frase. Las fronteras candidatas provienen de puntuación, salto de línea, conectores temporales y coordinación. Una frontera solo se acepta cuando el texto posterior inicia un predicado comercial distinto, cambia de sujeto con predicado, o la puntuación cierra una cláusula. `y` sin nuevo predicado permanece dentro del segmento para conservar listas de productos.

El orden original nunca cambia. Los límites iniciales son 2.000 caracteres y 20 segmentos; un exceso produce `BLOCKED`, no truncamiento silencioso.

## Adaptadores batch

Tres extensiones viven fuera del motor congelado:

1. deuda nueva explícita: conserva cliente + monto cuando ambos están en el mismo span;
2. venta con total explícito: permite `unit_price=null` y marca el total como `EXPLICIT`; no inventa precio unitario;
3. line items: solo si cada renglón contiene cantidad, producto y precio unitario inequívocos. El total es `DERIVED` con fórmula visible.

Si un adaptador no reconoce la forma completa, se conserva el resultado seguro de Engine 1.1.

## Grupos de transacción

La forma controlada `cliente llevó/compró TOTAL y pagó/dejó PAGO` puede producir un grupo `SALE_SETTLEMENT` con:

- venta por el total explícito;
- pago inmediato explícito;
- cuenta por cobrar derivada como `TOTAL - PAGO` cuando el resultado es positivo.

La diferencia lleva `derived=true`, fórmula y campos fuente. `dejó` requiere el marco lingüístico de compra y una revisión humana; aislado no equivale automáticamente a pago. Un pago mayor al total bloquea el grupo.

## Contexto y dependencias

Las referencias entre segmentos solo se propagan dentro del batch, con `source_segment_id`, `source_entity`, confianza y alcance. Un pago posterior puede depender de una deuda creada antes en el mismo batch. La dependencia se registra explícitamente y se persiste en orden topológico; no se resuelve coreferencia libre (`ella`, `la señora`) sin antecedente único.

## Confirmación

- `CONFIRM_SAFE_ITEMS` confirma exactamente el conjunto de ítems `COMPLETE` solicitado.
- `REVIEW_ALL` no persiste nada.
- “Confirmar todo” se ofrece únicamente cuando todos los ítems son confirmables.
- Una clave de idempotencia identifica el batch completo y una clave derivada identifica cada ítem.
- La operación, grupo, ledger, movimientos de deuda y audit trail se escriben en una sola transacción SQLite.
- Cualquier fallo revierte el conjunto completo solicitado.

## Compatibilidad

`POST /pilot/interpret` y las operaciones históricas conservan compatibilidad. El endpoint experimental `POST /pilot/interpret-batch` se habilita solo mediante una variable de entorno y permanece apagado en P01_R3. Las ventas históricas se leen como antes; un adaptador puede representarlas como un solo line item en respuesta sin reescribir su JSON.

## UX del cuaderno batch

- **Persona:** comerciante en movimiento, con pocos segundos y una narración recién ocurrida.
- **Tarea:** detectar, revisar y confirmar varios movimientos sin mezclar dinero.
- **Sensación:** cuaderno sereno, verificable y más cercano a renglones contables que a un dashboard.
- **Dominio:** movimientos, renglones, fiados, abonos, saldos, comprobantes.
- **Color:** papel crema, tinta carbón, sello verde, lápiz terracota, alerta ámbar.
- **Firma:** tira de procedencia que resalta el fragmento exacto que originó cada ítem.
- **Profundidad:** bordes suaves y cambios de superficie; sin sombras decorativas.
- **Escala:** base de 4 px, controles táctiles mínimos de 44 px.

La vista muestra el conteo de listos y pendientes, tarjetas expandibles en orden narrativo, edición localizada, origen textual y acciones separadas. El estado siempre incluye texto/icono además de color.

## Gates

La evaluación natural de 100 narrativas está en [`BATCH_NATURAL_DEVELOPMENT_EVALUATION.md`](../evaluation/BATCH_NATURAL_DEVELOPMENT_EVALUATION.md): cero violaciones/crossovers y spans 100%, pero el benchmark web-derived conserva baja recuperación. Por ello `BATCH_GENERALIZATION_HOLD` y la bandera de piloto continúa apagada.

### Verificación local del 30-08-2026

- flujo sintético móvil: acceso, consentimiento, lote mixto, éxito parcial, confirmación de 2 seguros e historial;
- viewports: 320, 375, 390, 430 y 1280 px sin overflow horizontal;
- touch targets observados: mínimo 44 px;
- labels, headings, regions, estados live y navegación por teclado presentes;
- consola del navegador: 0 warnings/errors durante el flujo;
- dictado: Web Speech inició/canceló en el navegador de laboratorio, pero no se produjo audio físico ni se midió transcripción; el gate de voz permanece en hold.

Rendimiento local del intérprete, 100 repeticiones por tamaño: 2 movimientos mediana/p95/peor `0,37/0,51/0,79 ms`; 5 `0,78/1,39/1,84 ms`; 10 `1,44/1,67/1,94 ms`; 20 (dos narrativas de 10 concatenadas solo para carga) `2,86/3,28/3,62 ms`. Son mediciones de desarrollo, no un SLA.

El gate exige regresiones históricas verdes, cero violaciones financieras críticas, segmentación y partial success medibles, ledger consistente, confirmación atómica/idempotente, aislamiento por participante, UX móvil y CI verde. Este gate no autoriza deployment ni voz de campo.
