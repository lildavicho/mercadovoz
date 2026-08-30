# Análisis de errores y vacíos — P01 Round 1

## Límite de evidencia

P01 Round 1 no contiene correcciones, confirmaciones, rechazos, cancelaciones ni anotaciones humanas. Por ello no existe una taxonomía de errores semánticos observados con ground truth. Este documento clasifica vacíos del proceso y cambios del replay, no frases como “correctas” o “incorrectas”.

## Hallazgos observables

| Clase | Evidencia | Severidad | Acción generalizable |
|---|---|---|---|
| `UX` / outcome ausente | 25 inputs y 0 outcomes terminales | P0 de evaluación | Hacer explícito el cierre por confirmar, corregir, rechazar o cancelar; mantener auditoría. |
| `SCHEMA_GAP` / ronda implícita | R1 dependía de versión/fecha para separar captura | P0 de integridad | Persistir `round_id` en sesiones y eventos; backfill reproducible. |
| `SECURITY` / transporte | Captura inicial ocurrió por HTTP temporal | P0 de privacidad | No abrir R2 hasta HTTPS válido y credenciales rotadas. |
| `COMPOUND` | 5 estados compuestos iniciales | Riesgo técnico | Conservar la abstención y evaluar el soporte generalizado del motor nuevo. |
| `CONTEXT` | 7 estados `NEEDS_CONTEXT`; 3 eventos explícitos de contexto | Riesgo UX | Medir si la solicitud puede resolverse sin inventar cliente/campo. |
| `PERFORMANCE` | mediana 0,296 ms; p95 4,1704 ms | Bajo en motor | Mantener medición; no confundirla con tiempo total de registro. |

## Replay: cambios que requieren evidencia futura

El replay de 25 textos con Engine 1.1 produjo 17 resultados equivalentes y 8 cambios. Cuatro cambios corresponden a límites técnicos conocidos, dos a una abstención más segura ante compuestos, uno elimina un pronombre como cliente y uno reconoce un cliente nombrado pero carece de ground truth. Estas etiquetas describen comportamiento del software; solo la última operación aceptada/corregida por el humano puede informar el outcome de desarrollo.

## Qué no se hará

- No crear regex por frase.
- No etiquetar `CONFIRMATION_SHOWN` como aceptación.
- No mezclar replay 1.1 con la captura 1.0.
- No atribuir el abandono a un motivo no observado.
- No autorizar voz o LLM a partir de estos datos.

## Instrumentación para R2

R2 debe conservar `input_id`, versiones y `round_id`; impedir dobles confirmaciones; registrar correcciones estructuradas; y producir exactamente un outcome terminal cuando el participante confirme, corrija y confirme, rechace o cancele. Una sesión abandonada seguirá cerrándose como cierre administrativo, nunca como outcome humano.
