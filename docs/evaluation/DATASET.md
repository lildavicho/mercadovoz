# Dataset

## Formato

Cada línea JSON contiene `id`, `text`, `expected` y `metadata` opcional. `expected` usa el mismo sobre del parser: `status` y `operation`. Una operación parcial en un caso ambiguo contiene únicamente lo que puede afirmarse a partir de la frase.

```json
{"id":"mv-001","text":"Vendí tres cajas de tomate a catorce cada una","expected":{"status":"COMPLETE","operation":{"type":"SALE","product":"tomate","quantity":3,"unit":"caja","unit_price":14,"total":42}},"metadata":{"source":"synthetic","tier":"core"}}
```

`metadata.correction_text` y `metadata.expected_after_correction` definen una prueba de recuperación. Otras etiquetas describen casos ambiguos, expresiones locales, operaciones compuestas o intenciones exploratorias; no cambian la respuesta esperada.

## Separación

- [`development.jsonl`](../../research/benchmarks/synthetic/development.jsonl): 40 casos para construir y depurar reglas.
- [`evaluation.jsonl`](../../research/benchmarks/synthetic/evaluation.jsonl): 30 casos retenidos y congelados antes de la ejecución final; incluye 6 correcciones.

Ningún resultado de desarrollo se presenta como evaluación independiente. El conjunto retenido actual es útil como prueba de regresión, pero **no es evidencia externa**: también es sintético y comparte el vocabulario y los supuestos del laboratorio. Después de ejecutar la evaluación el 28 de agosto de 2026 no debe editarse para mejorar la cifra; cualquier cambio exige una nueva versión del corpus y debe conservar el resultado anterior.

## Privacidad y procedencia

Los datos actuales son inventados y usan nombres ficticios. No contienen teléfonos, cédulas, direcciones, información bancaria ni nombres completos reales.

Para incorporar datos reales:

1. Obtener consentimiento separado para frase/transcripción y, si aplica, audio.
2. Sustituir personas, negocios y ubicaciones por marcadores o nombres ficticios antes de guardar.
3. Conservar la frase tal como fue pronunciada o transcrita; no “corregir” su gramática.
4. Etiquetar procedencia, contexto de ruido, tipo de negocio y método de transcripción sin identificar a la persona.
5. Separar por participante, de modo que frases de una misma persona no queden simultáneamente en desarrollo y evaluación.
6. Congelar al menos 25% antes de cambiar reglas, prompts o schemas.

## Próxima muestra mínima

Recolectar 50–100 frases de 6–8 participantes de un solo tipo de negocio. Debe haber operaciones completas, frases incompletas, correcciones, expresiones desconocidas y ejemplos que no son operaciones. La distribución debe registrarse; no se deben duplicar plantillas cambiando únicamente números, porque eso infla artificialmente la precisión.

El contrato privado está documentado en [`REAL_DATASET_SCHEMA.md`](../pilot/REAL_DATASET_SCHEMA.md) y [`REAL_EVALUATION.md`](REAL_EVALUATION.md). La separación es por participante completo con dos IDs held-out preasignados; nunca por frases individuales. El corpus sintético permanece sin cambios.
