# Política de procedencia monetaria

- `EXPLICIT`: el valor aparece en el texto. Ejemplo: total $3; puede persistirse con `unit_price=null`.
- `DERIVED`: el valor se calcula de campos explícitos. Ejemplo: `total=quantity*unit_price`; conserva fórmula y nunca se etiqueta como hablado.
- `CONTEXT_DERIVED`: el valor depende de contexto seleccionado y versionado. Debe registrar fuente/contexto y pedir confirmación.

Para ventas, `product`, `quantity`, `unit` y `total` forman un registro financieramente válido. `unit_price` es opcional si el total fue explícito. Si cantidad, precio unitario y total coexisten, deben ser consistentes dentro de un centavo. Una aproximación, autocorrección no resuelta o base de precio ambigua no produce valor exacto confirmable.
