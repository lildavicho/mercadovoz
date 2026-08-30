# Preparación de P01 Round 3

**Estado:** `P01_R3_PREPARED_NOT_STARTED`

Condiciones previas: release candidate 1.2 mergeado, CI verde, lock/backup de despliegue, migración 004 verificada, Engine/Schema visibles en `/pilot/config`, flags batch/voice apagadas, credencial rotada y consentimiento `pilot-consent-v1` aceptado en una nueva sesión.

P01_R3 seguirá siendo `REAL_DEVELOPMENT`. No reutilizará sesiones de R2 ni escribirá replay en evidencia histórica. La ronda no empieza con este documento ni con el deploy: empieza únicamente cuando P01 obtiene acceso, acepta consentimiento y crea una sesión `round_id=P01_R3`.

Objetivo: obtener outcomes terminales naturales suficientes para medir corrección y fricción del flujo texto individual. No solicitar batch ni voz. Próximo gate de campo: `P01_R3_MINIMUM_TERMINAL_OUTCOMES_AND_CLOSE`.
