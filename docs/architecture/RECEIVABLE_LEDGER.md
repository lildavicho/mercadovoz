# Ledger de cuentas por cobrar — Engine 1.2 experimental

## Modelo

Una deuda nueva crea una fila `receivables`, una operación `RECEIVABLE` y un movimiento inmutable `CREATED`. Un abono crea una operación `PAYMENT_RECEIVED`, una `payment_allocation` explícita y un movimiento `PAYMENT`. El saldo se calcula y persiste en centavos enteros; la presentación vuelve a dólares.

```text
RECEIVABLE operation -> receivable OPEN -> movement CREATED
PAYMENT_RECEIVED -----> allocation ------> movement PAYMENT -> OPEN | PAID
```

## Invariantes

- `original_amount > 0`, `0 <= balance <= original_amount`.
- Una deuda cerrada no recibe abonos ni se reabre implícitamente.
- Cliente del abono y cliente de la deuda deben coincidir tras normalización conservadora.
- Con dos deudas abiertas del mismo cliente se exige `receivable_id`; no se elige “la última”.
- Un abono superior al saldo se rechaza completo. No se recorta, reparte ni transforma en crédito.
- Operación, asignación, nuevo saldo, movimiento y auditoría comparten una transacción SQLite.
- Cada reintento usa una clave idempotente durable; una misma clave con otra selección se rechaza.

## Casos cubiertos

Abono parcial, abono total, varios abonos, deuda ya cerrada, cliente incorrecto, múltiples deudas, sobrepago y rollback inyectado en el segundo movimiento. La migración es aditiva; las operaciones históricas siguen legibles.

La migración 003→004 fue ejecutada sobre una copia del SQLite real predeploy: preservó 4 sesiones, 148 eventos y 3 operaciones, y añadió únicamente las estructuras de batch/ledger. La política de downgrade es restaurar el backup pre-migración; no se ejecutan migraciones destructivas inversas.

## Límite

No hay refinanciación, saldo a favor, reversos contables ni reparto automático entre varias deudas. Esos casos requieren diseño y evidencia de campo, no heurísticas.
