# Preparación de P01 Round 3

**Estado:** `P01_R3_READY_NOT_STARTED`

Condiciones técnicas cumplidas: release 1.2 mergeado, CI verde, lock/backup de despliegue, migración 004 verificada, Engine/Schema visibles en `/pilot/config`, flags batch/voice apagadas y credencial rotada. El consentimiento `pilot-consent-v1` aún no fue aceptado en R3 porque no se inició una sesión humana.

P01_R3 seguirá siendo `REAL_DEVELOPMENT`. No reutilizará sesiones de R2 ni escribirá replay en evidencia histórica. La ronda no empieza con este documento ni con el deploy: empieza únicamente cuando P01 obtiene acceso, acepta consentimiento y crea una sesión `round_id=P01_R3`.

Objetivo: obtener outcomes terminales naturales suficientes para medir corrección y fricción del flujo texto individual. No solicitar batch ni voz. Próximo gate de campo: `P01_R3_MINIMUM_TERMINAL_OUTCOMES_AND_CLOSE`.
