# Métricas congeladas — `pilot-metrics-v1`

## North star

`SUCCESSFUL_REGISTRATION_RATE = OPERATION_CONFIRMED / TEXT_SUBMITTED`

El denominador incluye cada envío no vacío dentro de una sesión consentida que intenta registrar una operación. Incluye rechazados, cancelados, abstenciones y propuestas que piden contexto. Excluye intentos bloqueados antes de persistir `TEXT_SUBMITTED`, health checks, feedback y clicks. Un reintento técnico con el mismo `input_id` no debe crear un nuevo intento. Cambiar esta definición exige otra versión antes de mirar resultados.

## Métricas reproducibles

- `TOTAL_INPUTS`: eventos `TEXT_SUBMITTED`.
- `PROPOSAL_RATE`: inputs con propuesta / inputs.
- `CONFIRMATION_RATE`: inputs confirmados / inputs.
- `CORRECTION_RATE`: inputs con ≥1 corrección / inputs.
- `REJECTION_RATE`: rechazados / inputs.
- `CANCELLATION_RATE`: cancelados / inputs.
- `CONTEXT_REQUEST_RATE`: inputs con contexto solicitado / inputs.
- `SAFE_ABSTENTION_RATE`: inputs sin operación y estado seguro / inputs.
- `CRITICAL_FINANCIAL_ERROR_RATE`: inputs anotados críticos / inputs revisados.
- `TIME_TO_REGISTER`: `TEXT_SUBMITTED` a resultado terminal; reportar mediana y p95.
- `MEDIAN_CONFIRMATION_TIME`: `CONFIRMATION_SHOWN` a `OPERATION_CONFIRMED`.
- `OPERATIONS_PER_SESSION`: confirmadas / sesiones iniciadas.

## Error financiero crítico

Es crítico si ocurre al menos uno: monto equivocado confirmado sin advertencia; deuda nueva desde una frase de estado; abono al cliente incorrecto; gasto personal convertido silenciosamente en comercial; compuesto reducido silenciosamente; aproximación convertida en exacta; operación duplicada por reintento.

La etiqueta requiere revisión del operador. `CONFIRMED` significa `USER_ACCEPTED_OPERATION`, no verdad perfecta.

## Targets previos a resultados

0 errores financieros críticos; registro exitoso ≥90%; manejo seguro ≥95%; corrección ideal ≤15%. Con P01 se reportan conteos y tamaño de muestra; un único participante no valida mercado ni invalida automáticamente el producto.
