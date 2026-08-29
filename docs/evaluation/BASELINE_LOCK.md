# Congelamiento del baseline sintético

**Fecha:** 28 de agosto de 2026  
**Estado de decisión:** `ITERATE`  
**Baseline:** parser determinista Python, sin modelo ni llamadas API

## Resultado congelado

| Evidencia | Valor |
|---|---:|
| Development sintético | 40 ejemplos |
| Held-out sintético | 30 ejemplos |
| Intent accuracy | 100% (29/29) |
| Field accuracy | 100% (80/80) |
| Exact operation accuracy | 100% (24/24) |
| Core exact operation accuracy | 100% (19/19) |
| Confirmation recovery | 100% (6/6) |
| Abstention precision / recall | 100% / 100% |
| Costo API | USD 0 |

El resultado completo es [`heldout-rules.json`](../../research/benchmarks/results/heldout-rules.json). Estas cifras son sintéticas y no estiman el desempeño con comerciantes reales.

## Archivos congelados y SHA-256

```text
f3d2ab4cb119fb508a34e9cb0f8b16a797905bf0aecf137dfc840cf8ee2284d8  engine/src/mercadovoz/parser.py
7325879190f905b980cfa1e8bac6320fe810d3a1a2436f2e6836e71c6ed6e7f9  engine/src/mercadovoz/numbers.py
7830fa9a50d6ae9e1b0c7cf6b1b9193cae4c4a06843ac6958699b74d527b9565  engine/src/mercadovoz/models.py
e57bf228d8d3bebc5bd79b2d09218f84348f5e4fda8e9ec107d016c6bb024f04  engine/src/mercadovoz/corrections.py
bbf3a281a174981afe16937b46056edbb253196597c5fe507df0663ddb124379  engine/src/mercadovoz/evaluation.py
cdc0441805457f62ae0928126a517d6bfb2d4d51f30ced88c7823691bdac4383  research/benchmarks/synthetic/development.jsonl
8b0819a9cc43e0829a96b08cf687a5e4a39bf256cb2e76228cd3070e92a393ce  research/benchmarks/synthetic/evaluation.jsonl
e55d21d769156c87143a58e6822130702fe3b1900008f5c9135d91b0c1005085  research/benchmarks/results/heldout-rules.json
```

Antes de evaluar datos reales se deben recalcular estos hashes. Cualquier diferencia invalida la etiqueta “baseline v0” hasta explicar el cambio.

## Regla de congelamiento

Hasta guardar `data/private/real-baseline-v0.json` no se modifican reglas, expresiones, unidades, normalización, schemas operativos, correcciones ni evaluador sintético. Tampoco se consulta el resultado por frase para ajustar el parser. Los archivos nuevos de Sprint 0.5 solo capturan, validan el formato, separan participantes y ejecutan el baseline existente.

No se creó tag porque `C:\ideas` no es un repositorio Git. No se inicializó repositorio y no se hizo push.

## Verificación previa P00-WEB

El 29 de agosto de 2026, antes de ejecutar el corpus exploratorio, los ocho hashes anteriores coincidieron (`PASS 8/8`). P00-WEB se ejecutó sin cambios del baseline y quedó separado en [`p00-web-baseline-v0.json`](../../research/benchmarks/results/p00-web-baseline-v0.json).

## Verificación previa P01-WEB-DERIVED

El 29 de agosto de 2026, antes de ejecutar la simulación de campo web-derived, los ocho hashes coincidieron nuevamente (`PASS 8/8`). El resultado separado está en [`p01-web-derived-baseline-v0.json`](../../research/benchmarks/results/p01-web-derived-baseline-v0.json); no es held-out ni evidencia de usuario.
