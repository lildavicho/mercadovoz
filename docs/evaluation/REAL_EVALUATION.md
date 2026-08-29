# Evaluación del corpus real — protocolo previo

## Estado

El corpus está vacío y no se han inventado participantes ni frases. La primera ejecución todavía no existe. El baseline sintético permanece congelado según [`BASELINE_LOCK.md`](BASELINE_LOCK.md).

## Registro JSONL

Cada línea del export privado descrito en [`REAL_DATASET_SCHEMA.md`](../pilot/REAL_DATASET_SCHEMA.md) debe ser un objeto JSON independiente con:

```json
{
  "participant_id": "P__",
  "utterance_id": "P__-___",
  "text_original": "texto ya redactado, sin identificadores reales",
  "text_anonymized": "texto que recibirá el parser",
  "context": "situación observada o relatada",
  "expected_status": "COMPLETE | NEEDS_CONFIRMATION | UNRECOGNIZED",
  "expected_operation": null,
  "expected_fields": [],
  "unknown_language_categories": [],
  "notes": ""
}
```

Para una operación conocida, `expected_operation` contiene el objeto esperado y `expected_fields` enumera exactamente sus claves. Los campos opcionales `correction_text_anonymized` y `expected_after_correction` permiten medir recuperación solo cuando la corrección ocurrió en la prueba. El JSON es un contrato ilustrativo con marcadores, no una frase ni un participante real; no debe copiarse como registro.

## Validación sin contaminar

Durante la captura solo validar estructura:

```powershell
python scripts\evaluation\evaluate_real_corpus.py data\private\real-development.jsonl --validate-only
```

Este modo no llama al parser. Antes de la primera evaluación se requieren 6–8 participantes y al menos 50 frases.

P01 es una excepción explícita para comprobar el pipeline como development, no como held-out. Después de terminar y etiquetar todas sus frases, se ejecutará:

```powershell
python scripts\evaluation\evaluate_real_corpus.py data\private\real-development.jsonl --development-pilot P01 --output data\private\p01-baseline-v0.json
```

El reporte marcará `evaluation_role: development_pilot`; sus métricas no pueden mezclarse con el futuro held-out real.

## Split obligatorio

La unidad de separación es el participante completo. Aplicar la tabla predefinida en [`FIELD_PROTOCOL.md`](../pilot/FIELD_PROTOCOL.md). No dividir frases al azar, no mover una persona para mejorar balance y no observar predicciones held-out antes de congelar gold labels.

Ejemplo de comando si terminan ocho participantes:

```powershell
python scripts\evaluation\evaluate_real_corpus.py data\private\real-heldout.jsonl --heldout-participants P04 P08 --output data\private\real-baseline-v0.json
```

Para seis usar `P03 P06`; para siete, `P03 P07`. El script evalúa solo esos participantes y registra cuáles quedaron en development sin ejecutar sobre ellos.

## Métricas adicionales

- **Recognition coverage:** porcentaje held-out con una operación reconocida, aunque requiera confirmación.
- **Complete coverage:** porcentaje held-out devuelto como `COMPLETE`.
- **Unknown language rate:** porcentaje con al menos una categoría humana de lenguaje desconocido.
- Conteo por `UNKNOWN_UNIT`, `UNKNOWN_EXPRESSION`, `IMPLICIT_AMOUNT`, `COMPOUND_OPERATION`, `OUT_OF_SCOPE_INTENT`, `AMBIGUOUS_REFERENCE`, `UNEXPECTED_STRUCTURE`, `ABBREVIATION` y `OTHER`.

El reporte conserva intent, campos, exactitud, core exact, abstención, correcciones, latencia y costo del evaluador original. También incorpora una comparación directa contra la referencia sintética. Una caída, incluso a 55%, se conserva sin editar frases ni reglas.

## Gate posterior

`GO` requiere inicialmente ≥80% core exact held-out real, ≥90% tras corrección, ambigüedad segura, cuatro comerciantes dispuestos a otra prueba y evidencia de problema frecuente. `ITERATE`, `REDUCE SCOPE`, `PIVOT` o `KILL` se deciden con el patrón técnico y la evidencia de comportamiento, no solo con un promedio.

## Resumen de validación de producto — completar después

No completar con impresiones generales: contar fichas con evidencia concreta y enlazar los códigos de participante.

| Pregunta | Resultado pendiente | Evidencia/códigos |
|---|---|---|
| Participantes con problema frecuente (`pain_level` 2–3) | — / total | |
| Registran ventas | — / total | |
| Registran gastos | — / total | |
| Registran fiados/cuentas por cobrar | — / total | |
| Tienen olvidos frecuentes | — / total | |
| Aceptan una segunda prueba concreta | — / total | |
| Operación más repetida | pendiente | |
| Operación más dolorosa | pendiente | |
| Flujo inicial con mayor valor | pendiente | |

Registrar aquí si la evidencia favorece fiados, ventas, gastos, cierre diario u otro flujo más pequeño. No preservar “mini ERP” por inercia.

## Decisión pendiente

- Resultado: `GO / ITERATE / REDUCE SCOPE / PIVOT / KILL`
- Evidencia técnica decisiva:
- Evidencia de problema decisiva:
- Riesgo dominante:
- Próximo experimento permitido:

No probar reglas v2, LLM o híbrido hasta guardar y analizar `real-baseline-v0.json`.
