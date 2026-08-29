# Confirmación y correcciones controladas

El parser nunca equivale a “guardar”. Una respuesta `COMPLETE` contiene una pregunta legible que resume intención, cantidades y total. La futura interfaz deberá esperar `sí`, cancelación o una corrección antes de persistir.

Las correcciones soportadas en el laboratorio son `quantity`, `unit_price`, `amount`, `unit`, `customer` y `product`. Se aplican sobre el resultado JSON pendiente, no sobre un historial ni una conversación abierta. Al cambiar cantidad o precio se recalcula el total; al cambiar importe en gastos/deudas/abonos se modifica únicamente `amount`.

Ejemplo:

```text
Entrada:     Vendí cinco cajas de tomate a doce.
Propuesta:   5 cajas, tomate, $12/unidad, total $60.
Corrección:  No, eran seis cajas.
Resultado:   6 cajas, tomate, $12/unidad, total $72.
```

Una corrección no reconocida conserva la propuesta, añade `correction_not_understood` y vuelve a pedir una corrección explícita. Una operación compuesta no se corrige como una sola operación: se solicita dividirla.

Límites: no hay resolución de pronombres libre, memoria conversacional, confirmación por voz ni persistencia. Esas capacidades solo se evalúan después de validar este contrato.
