# Grupos de transacción — schema v1

## Propósito

Una narrativa puede describir un solo evento comercial con varios movimientos contables. `transaction_group` conserva esa unidad sin colapsarla en una operación falsa.

El patrón soportado en v1 es `SALE_SETTLEMENT`:

```text
“María llevó $8 de producto y dejó $5”
  group SALE_SETTLEMENT
  ├─ SALE total=8
  ├─ PAYMENT_RECEIVED amount=5 role=PAYMENT_AT_SALE
  └─ RECEIVABLE amount=3 (derivado: 8 - 5)
```

Cada miembro conserva el mismo `source_span`, su `segment_id`, `transaction_group_id`, dependencias y procedencia de campos. Los movimientos dependientes no pueden confirmarse sin el movimiento fuente dentro de la misma confirmación.

## Confirmación y éxito parcial

- Los renglones independientes seguros pueden confirmarse juntos.
- Los pendientes, ambiguos, rechazados o cancelados no se guardan.
- Un grupo dependiente se valida como conjunto; no se permite una deuda derivada sin su venta.
- Toda selección se confirma atómicamente o no produce ninguna operación.

## Line items

Una venta con varios productos y bases unitarias explícitas es una sola `SALE` con `line_items`. El total se deriva de `sum(quantity * unit_price)` y queda marcado como `DERIVED`. No se inventan precios faltantes ni se convierte una lista de productos ambigua en renglones.

## Fuera de alcance

Compras, inventario completo, impuestos, devoluciones, descuentos y asignación entre varias deudas permanecen fuera de v1.

## Verificación

Las pruebas cubren `10 = 6 + 4` en centavos enteros, dependencias, confirmación idempotente, reintento y rollback total ante un fallo inyectado. Un grupo inválido no deja una venta, abono o deuda parcial en el ledger.
