# P00-WEB — análisis del baseline v0

## Condición metodológica

`P00-WEB` contiene 25 paráfrasis exploratorias derivadas de investigación pública. No son citas, entrevistas ni evidencia de usuario. `real_participant=false`, `source_type=WEB_DERIVED_EXPLORATORY`, rol `exploratory_web` y `eligible_for_real_metrics=false` quedaron registrados en el corpus y el resultado.

No se incorporó ninguna entrada a `REAL_DATASET_TEMPLATE.jsonl`. P01 sigue vacío y pendiente. Este resultado no participa en held-out, accuracy real, GO gate ni autorización de Sprint 1.

## Reproducibilidad

Antes de ejecutar el parser el 29 de agosto de 2026 se verificaron los ocho hashes de [`BASELINE_LOCK.md`](BASELINE_LOCK.md): **PASS 8/8**. No cambiaron parser, números, modelos, correcciones, evaluador base, datasets sintéticos ni resultado sintético.

```text
621cf37e691ce6ba6faddfe64e6b9fe4bba323c7451d6d5bdd7c42330370827a  research/benchmarks/web-derived/P00_WEB_CORPUS.jsonl
76b85b1c4902507c7103adbe78f18683d05d388c4ab9d9666f9c41250c46358e  research/benchmarks/results/p00-web-baseline-v0.json
```

Comando ejecutado:

```powershell
python scripts\evaluation\evaluate_real_corpus.py research\benchmarks\web-derived\P00_WEB_CORPUS.jsonl --exploratory-corpus P00-WEB --output data\runtime\p00-web-check.json
```

## Métricas descriptivas

| Métrica | P00-WEB | Referencia sintética | Uso permitido |
|---|---:|---:|---|
| Intent accuracy | 57,9% (11/19) | 100% | diagnóstico, no accuracy real |
| Field accuracy | 25,5% (12/47) | 100% | diagnóstico |
| Exact operation accuracy | 14,3% (1/7) | 100% | diagnóstico |
| Core exact accuracy | 0% (0/4) | 100% | diagnóstico |
| Abstention precision | 72,7% | 100% | seguridad exploratoria |
| Abstention recall | 88,9% | 100% | seguridad exploratoria |
| Recognition coverage | 60% (15/25) | no calculada | descripción |
| Complete coverage | 12% (3/25) | no calculada | descripción |
| Unknown language rate | 96% (24/25) | no aplica | construido adversarialmente |

No hubo correcciones conversacionales, por lo que confirmation recovery es `null`. La comparación no es estadística: P00-WEB fue diseñado para concentrar ambigüedad, contexto implícito y gaps.

## Qué hizo bien

- `P00-WEB-006`: reconoció pago y pidió cliente/importe en lugar de inventarlos.
- `P00-WEB-012`: única operación completa exacta, ajuste de tres libras de tomate.
- `P00-WEB-014`, `015` y `021`: dejó fuera agregados aproximados o aporte personal no modelado.
- `P00-WEB-022`: detectó que había más de una operación y pidió separarlas. El evaluador marca una operación parcial como discrepancia, pero la conducta de abstención es segura.
- `P00-WEB-023`: no inventó cantidad o precio de “todo”; pidió campos, aunque extrajo mal el producto.

Solo 1 de 3 operaciones compuestas recibió la advertencia específica. Tres de cinco casos esperados fuera de alcance quedaron realmente `UNRECOGNIZED`.

## Errores y disposición

| ID y frase | Esperado | Obtenido | Categoría / causa probable | ¿Corregir? | Confirmación / scope |
|---|---|---|---|---|---|
| 001 · “vendí cinco libras de tomate a dos dólares” | confirmar unitario vs total | `COMPLETE`, $2/u, total $10 | `AMBIGUOUS`, `PARSER_RULE_GAP` | no con una regex aislada | preguntar significado de $2; dentro del scope |
| 002 · “se fueron tres fundas…” | venta completa | `UNRECOGNIZED` | `UNKNOWN_EXPRESSION`, `PARSER_RULE_GAP` | solo si lenguaje real lo repite | reconocer y confirmar; scope core |
| 003 · “me llevó dos cajas y me pagó veinte” | venta parcial, producto implícito | pago recibido sin campos | `WRONG_INTENT`, `IMPLICIT_REFERENCE` | requiere contexto, no keyword aislada | confirmar producto/total; scope core |
| 004 · “[NOMBRE] quedó debiendo doce” | cuenta por cobrar completa | falta cliente | `MISSING_FIELD`, artefacto de anonimización | no adaptar producto a corchetes | confirmar cliente; scope core |
| 005 · “[NOMBRE] me abonó cinco” | abono completo | faltan cliente e importe | `MISSING_FIELD`, artefacto de placeholder/patrón | no todavía | confirmar ambos; scope core |
| 007 · “gasté cuatro en el almuerzo” | confirmar negocio vs personal | gasto completo; categoría “el almuerzo” | `SCHEMA_GAP`, `WRONG_PRODUCT` semántico/canonización | no antes de evidencia real | confirmar naturaleza; posible retiro personal |
| 008 · “pagué seis del transporte” | gasto completo | `UNRECOGNIZED` | `UNEXPECTED_STRUCTURE`, `PARSER_RULE_GAP` | patrón plausible, esperar P01+ | scope core |
| 009 · “compré una caja… en quince” | compra completa | producto incluye “en 15”; faltan precios | `WRONG_PRODUCT`, `MISSING_FIELD`, conector no soportado | solo con repetición real | confirmar total; exploratorio |
| 010 · “traje dos sacos…” | compra completa | `UNRECOGNIZED` | `UNKNOWN_EXPRESSION`; traje puede ser compra o stock | no mapear directamente | preguntar compra vs entrada; exploratorio |
| 011 · “me quedan cuatro cajas” | stock parcial conocido | detecta stock pero omite cantidad/unidad/modo | `MISSING_FIELD`, extracción todo-o-nada | candidato generalizable después del baseline real | confirmar producto; exploratorio |
| 013 · “salieron diez fundas hoy” | venta parcial | `UNRECOGNIZED` | `UNKNOWN_EXPRESSION`, `IMPLICIT_REFERENCE`, `IMPLICIT_AMOUNT` | no sin evidencia real | requiere producto/precio/contexto |
| 016 · “vendí dos a cinco y una quedó fiada” | venta parcial + deuda separada | producto inventado “a 6 quedó fiada” | `COMPOUND_OPERATION`, `WRONG_NUMBER`, `WRONG_PRODUCT` | candidato de seguridad, no cambiar antes de P01 | separar y confirmar; scope múltiple |
| 017 · “[NOMBRE] llevó ocho y pagó cinco nomás” | venta $8 + deuda $3 | `UNRECOGNIZED` | `COMPOUND_OPERATION`, `UNKNOWN_EXPRESSION`, `SCHEMA_GAP` | no como regex única | separar; venta y receivable |
| 018 · “me debía quince y hoy dejó diez” | abono $10, cliente implícito | `UNRECOGNIZED` | `UNKNOWN_EXPRESSION`, `IMPLICIT_REFERENCE` | esperar lenguaje real | confirmar cliente/abono |
| 019 · “de los veinte… la mitad” | abono $10 | detecta pago, omite importe | `IMPLICIT_REFERENCE`, `MISSING_FIELD`, aritmética | no necesita adivinar | confirmar cálculo/cliente |
| 020 · “saqué cinco dólares… de la casa” | retiro personal fuera de scope | ajuste de stock | `WRONG_INTENT`, `SCHEMA_GAP`, polisemia de “saqué” | prioridad de seguridad si aparece en real | no guardar como stock; fuera de scope actual |
| 022 · “me dieron treinta… y gasté ocho…” | dos operaciones; separar | `NEEDS_CONFIRMATION` con warning compuesto | `COMPOUND_OPERATION`; conducta principal correcta | no corregir extracción aún | separar; ambas core |
| 023 · “vendí todo el tomate que quedaba” | venta parcial | producto “todo el tomate que quedaba” | `WRONG_PRODUCT`, `IMPLICIT_AMOUNT` | contexto de stock antes que regex | confirmar cantidad/precio |
| 024 · “[NOMBRE] todavía me debe lo de ayer” | estado existente, no crear operación | receivable parcial | `WRONG_INTENT`, `OUT_OF_SCOPE_INTENT`, `SCHEMA_GAP` | requiere semántica de evento/estado | no duplicar deuda; consulta/estado |
| 025 · “anota que [NOMBRE] ya pagó” | liquidación con importe implícito | `UNRECOGNIZED` | `UNKNOWN_EXPRESSION`, `IMPLICIT_AMOUNT`, `IMPLICIT_REFERENCE` | requiere deuda activa | confirmar saldo/cliente |

En 016, la normalización transforma literalmente `cinco y una` en `6`, porque une palabras numéricas a través de la conjunción: `vendi 2 a 6 quedo fiada`. Es un riesgo algorítmico generalizable, pero se conserva intacto para que P01 mida el mismo baseline v0.

## Gaps del schema e interacción

No cambiar aún el schema. P00-WEB propone verificar con personas reales:

1. `OWNER_WITHDRAWAL` y `OWNER_CONTRIBUTION` para separar dinero personal/negocio.
2. Agregados de cierre, aproximaciones y límites, que no son operaciones exactas.
3. Estado de una deuda existente versus creación de una nueva deuda.
4. Liquidación/abono cuyo monto vive en una deuda activa.
5. Gasto empresarial versus personal.
6. Varias operaciones en una frase.
7. Contexto activo de cliente, producto, deuda o stock.

Esto sugiere que parte del problema no es “más comprensión de texto”, sino estado conversacional acotado y confirmaciones referidas a una operación/deuda activa.

## Recomendación técnica

**CONTINUE FIELD VALIDATION — KEEP BASELINE FROZEN.**

No crear Rules V1 ni introducir LLM a partir de P00-WEB. Usar estos hallazgos para observar en P01: significado de `a`/`en`, referencias implícitas, pagos parciales, estado de deuda, dinero personal y frases compuestas. Ejecutar primero `p01-baseline-v0.json` con los mismos hashes. Después decidir si los patrones corroborados justifican reglas generales, cambios de schema, contexto controlado o un comparador híbrido posterior.
