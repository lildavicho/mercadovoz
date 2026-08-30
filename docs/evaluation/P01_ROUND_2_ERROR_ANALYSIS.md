# Análisis de errores de P01 Round 2

| Categoría | Evidencia observada | Causa general | Resolución 1.2 |
|---|---|---|---|
| `CUSTOMER_EXTRACTION` / `RECEIVABLE_CONTEXT` | una deuda nueva con cliente explícito perdió ese campo | el parser legado extraía monto, pero la gramática explícita no cubría la familia `nombre + quedó debiendo` | regla general con variantes de nombres/montos; estados de deuda existente siguen bloqueados |
| `TOTAL_WITHOUT_UNIT_PRICE` / `SCHEMA_GAP` | una venta con total explícito exigía precio unitario | `SALE` requería redundante `unit_price` aun con total válido | `total` explícito es suficiente; `unit_price=null`, nunca inventado |
| `UX_CONFIRMABILITY` | `NEEDS_CONTEXT` podía mostrar “Confirmar y registrar” | la UI dependía de existencia de propuesta, no de estado completo | contrato `isConfirmableProposal`; confirmación oculta y API rechaza 409 |
| `COMPOUND` | 5 entradas quedaron compuestas | Engine 1.1 era single-operation | batch continúa detrás de bandera |
| `AMBIGUITY` / `SAFE_ABSTENTION` | aproximaciones y base de precio ambigua | incertidumbre real | se preserva abstención y se endurecen autocorrecciones/dudas |

No se creó una regla para María, naranjas, 12 o 3. Las pruebas cubren Rosa, Carlos, Juan y Ana; deuda nueva vs estado existente; total explícito; autocorrección; y API manipulada. Los 24 inputs sin outcome no se etiquetan como errores.
