# Protocolo de campo V2 — piloto privado en aplicación

## Clasificación

P01 Round 1 es `REAL_DEVELOPMENT`, nunca `REAL_HELDOUT`. El motor permanece congelado durante toda la ronda. P01 solo existe después de aceptar `consent-v1`; antes, `CURRENT_PARTICIPANTS = 0`.

## Antes de comenzar

El operador completa [`DEPLOYMENT_CHECKLIST.md`](../deployment/DEPLOYMENT_CHECKLIST.md), verifica versiones contra [`PILOT_ENGINE_LOCK.md`](PILOT_ENGINE_LOCK.md), confirma base sin demo/fixtures, prueba backup/restauración y entrega la invitación por un canal separado. No se consulta ningún dataset previo durante la sesión.

## Instrucción para P01

Usa MercadoVoz normalmente. Escribe lo que realmente habrías registrado en ese momento, con tus propias palabras. No intentes engañar al sistema, pero tampoco reformules para ayudarlo. Revisa siempre la tarjeta y corrige, rechaza o cancela si no corresponde. No inventes ventas, gastos, fiados o abonos para completar una cuota.

## Ronda 1

- mínimo: 30 operaciones reales válidas;
- preferible: 50–100 en varios momentos o días;
- clases naturales: `SALE`, `EXPENSE`, `RECEIVABLE`, `PAYMENT_RECEIVED` si ocurren;
- ausencia de una clase se registra como ausencia, no se fabrica;
- nunca cambiar parser/reglas/seguridad/contexto durante la ronda.

Para cada input la aplicación registra propuesta/abstención, contexto solicitado, corrección, outcome y tiempo. No se exige cuestionario por operación. Al cerrar sesión, feedback opcional: molestia, faltante, desconfianza y qué fue más rápido.

## Observación humana separada

El operador puede anotar si la persona vuelve a usarlo, registra algo antes omitido, lo considera más rápido, recupera una deuda, entiende el resumen o confía en confirmar. Estas señales no se infieren desde logs.

## Errores

Clasificar después de la sesión: `INTENT`, `AMOUNT`, `QUANTITY`, `UNIT`, `PRODUCT`, `CUSTOMER`, `CONTEXT`, `COMPOUND`, `STATE_VS_EVENT`, `PERSONAL_VS_BUSINESS`, `APPROXIMATION`, `CORRECTION`, `UX`, `PERFORMANCE`, `SCHEMA_GAP`, `OTHER`.

No hacer patch por frase. Agrupar causas y posponer cualquier cambio hasta cerrar el lock.

## Cierre de ronda

1. Terminar sesiones y detener nuevas invitaciones.
2. Ejecutar métricas y revisar manualmente errores críticos.
3. Exportar por script; no copiar filas a mano.
4. Calcular hashes y crear `REAL_DEVELOPMENT_LOCK.md` con participantes, sesiones, frases, fechas, versiones, exclusiones y consentimiento.
5. Completar [`P01_ROUND1_REPORT_TEMPLATE.md`](P01_ROUND1_REPORT_TEMPLATE.md).
6. Emitir exactamente un gate: `FIELD_ITERATE`, `FIELD_REDUCE_SCOPE`, `FIELD_CONTINUE`, `FIELD_SAFETY_HOLD` o `FIELD_KILL`.

No declarar `FIELD_VALIDATED`. Voz solo puede pasar de `VOICE_HOLD` si el texto funciona razonablemente y hay evidencia de fricción al escribir o preferencia clara por voz.

## Split futuro

P02–P08 requieren participación/autorización real. Reservar personas completas como held-out; nunca usar frases de una misma persona a ambos lados como única estrategia. No contactar automáticamente a nadie.
