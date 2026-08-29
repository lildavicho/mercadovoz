# Reporte de fuga de datos — external-cuenca-v1

## Método

Se compararon los 240 textos externos contra:

- synthetic development;
- synthetic heldout;
- P00-WEB;
- P01-WEB-DERIVED.

La normalización convierte palabras numéricas y dígitos en `<num>`, placeholders en `<persona>`, elimina tildes/puntuación y normaliza espacios. Se marca `LEAKAGE_RISK` cuando el skeleton es idéntico o cuando simultáneamente `SequenceMatcher ≥ 0,92` y Jaccard de tokens `≥ 0,80`.

## Resultado

| Coincidencia previa | Registros externos |
|---|---:|
| P00-WEB | 19 |
| P01-WEB-DERIVED | 56 |
| Sintético development/heldout | 0 |
| Total único | **75** |

Los 75 son coincidencias de skeleton exacto. No significa copia literal ni invalida el corpus completo: significa que esas estructuras ya influyeron en la capa v1 y no son evidencia independiente de generalización.

Ejemplos:

| Externo | Corpus previo | Riesgo |
|---|---|---|
| `[NOMBRE_A] me abonó 8` | `[NOMBRE] me abonó cinco` | mismo patrón tras normalizar persona/número |
| `saqué 8 para la casa` | `saqué cinco para la casa` | mismo patrón de retiro |
| `[NOMBRE_B] todavía debe lo de ayer` | `[NOMBRE] todavía debe lo de ayer` | mismo patrón estado/deuda |
| `vendí cinco y una quedó fiada` | misma frase en P01-WEB-DERIVED | coincidencia literal/estructural |

El detalle 1:1, texto, corpus previo y similitudes está en [`external-leakage-v1.json`](../../research/external-cuenca-v1/manifests/external-leakage-v1.json). Los IDs excluidos están en [`external-leakage-risk-v1.ids.txt`](../../research/external-cuenca-v1/manifests/external-leakage-risk-v1.ids.txt).

## Consecuencia

- Los 75 casos se mantienen para regresión y seguridad conocida.
- Se excluyen de métricas de generalización independiente.
- No se atribuye frecuencia real a la cantidad de repeticiones: el corpus es una derivación controlada.
- El heldout independiente efectivo queda en 36 casos y tiene cobertura parcial; cualquier GO debe expresarse como técnico y provisional.
