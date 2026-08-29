# Consentimiento breve — MercadoVoz `consent-v1`

## Texto mostrado antes de una sesión

**MercadoVoz está en piloto privado.**

Durante esta sesión guardaremos:

- lo que escribas para registrar una operación;
- la propuesta que muestre MercadoVoz;
- si confirmas, corriges, rechazas o cancelas;
- tiempos técnicos y errores necesarios para evaluar el piloto.

Usaremos esos datos para llevar tu registro durante la prueba y analizar cómo mejorar el sistema. MercadoVoz puede equivocarse: revisa siempre tipo, monto, producto, cantidad y cliente antes de confirmar.

No te pediremos cédula, teléfono, dirección, correo, datos bancarios, fotografías, ubicación precisa ni audio. Puedes dejar de participar y solicitar que se eliminen tus datos del piloto. Los respaldos pueden conservar una copia temporal según su ciclo técnico.

Al elegir **Acepto y empezar**, confirmas que entendiste esta prueba y aceptas participar. Si no aceptas, no se crea participante ni sesión.

## Registro mínimo

- `consent_given = true`
- `consent_version = consent-v1`
- `consented_at` en UTC
- `participant_id` pseudónimo

No se guarda firma, nombre real ni documento. Un cambio material del texto exige `consent-v2`; nunca sustituir silenciosamente la versión aceptada.
