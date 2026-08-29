# MercadoVoz

**Decisión 2026:** CONSTRUIR · **Rol:** producto principal · **Puntuación:** 80,0/100 · **Costo MVP:** $$

# Problema

Comerciantes pequeños registran ventas, gastos, inventario o crédito con papel, memoria, calculadora y mensajes. Los ERP y POS existentes pueden resolver contabilidad, pero exigen catálogo, formularios y aprendizaje que interrumpen una jornada de venta.

# Usuario

Comerciante o ayudante de mercado/tienda que opera desde teléfono Android y necesita registrar una operación en segundos. El primer segmento será un tipo de negocio con unidades repetibles; no “todos los pequeños negocios”.

# Cliente

El negocio individual paga; una asociación o administración de mercado puede financiar onboarding B2B2C. Usuario y cliente suelen coincidir, salvo planes colectivos.

# Propuesta

Un cuaderno operativo que escucha una frase, propone una operación estructurada, la confirma y permite corregirla. Responde preguntas sobre datos registrados mediante consultas deterministas.

# Diferenciador

Español ecuatoriano y vocabulario de mercado; unidades como caja, quintal, libra, atado y unidad; crédito informal; confirmación comprensible; tolerancia a ruido/conectividad; exportación. No es “un ERP con micrófono”.

# Competencia

- [Treinta](https://treinta.co/) ya ofrece caja, inventario, POS y contabilidad en Ecuador y otros países.
- [Contífico POS Móvil](https://play.google.com/store/apps/details?id=com.contifico.pos) cubre ventas e integración operativa ecuatoriana.
- [GESCO](https://gesco.ec/) combina ERP/CRM, SRI, WhatsApp e IA en Ecuador.
- [VoiceKhata](https://play.google.com/store/apps/details?id=com.voice_khata.app), [BolkeHisaab](https://bolkehisab.in/) y [Talkbooks](https://talkbooks.app/) prueban que voz/chat-first para comercio ya existe.

**Qué no existe validado:** adopción y precisión para comerciantes de Cuenca, sus expresiones, unidades, ruido y flujo de crédito. Esa es la hipótesis, no una ventaja adquirida.

# MVP

## MVP 2026

- Registrar venta, gasto, deuda y abono mediante voz o texto.
- Mostrar transcripción y operación propuesta antes de guardar.
- Corregir tipo, ítem, cantidad, unidad, precio y contraparte.
- Historial, resumen diario/semanal y cuentas por cobrar.
- Exportación CSV, respaldo y eliminación.

## V1

Catálogo opcional, entradas/salidas simples de inventario, multiusuario básico, notas de voz diferidas y plan de pago.

## V2

Integraciones con POS/facturación autorizada, WhatsApp, OCR de facturas y recomendaciones de reposición basadas en suficiente historial.

## No hacer todavía

Facturación SRI propia, contabilidad de doble partida visible, nómina, e-commerce, pagos, agente autónomo, predicción de demanda o 20 tipos de negocio.

# PoC inicial

Recolectar 50–100 frases consentidas/anonimizadas, reservar 25% sin usar para ajustes y evaluar operación completa y cada campo. Flujo Wizard-of-Oz: audio → transcripción → JSON → confirmación. Meta: ≥80% operación completa y ≥90% después de confirmación. Medir también tiempo frente a método actual.

## Resultado técnico de Sprint 0 — 28 de agosto de 2026

Se implementó el [laboratorio texto→operación](../../../experiments/mercado-voz-parser/README.md) con 40 casos de desarrollo, 30 sintéticos retenidos, esquema explícito, abstención y seis correcciones. El baseline de reglas alcanzó 100% en ese banco, costo API cero y latencia local media de 0,140 ms.

**Decisión:** `ITERATE`, confianza externa baja. El resultado valida la herramienta de medición, no la precisión con comerciantes. Quedan pendientes 6–8 entrevistas, 50–100 frases independientes, comparación temporal con el método actual y luego —por separado— ASR con ruido/acento. No iniciar Sprint 1 basándose en el corpus sintético.

**Sprint 0.5:** baseline v0 congelado y [kit de validación real preparado](../../../experiments/mercado-voz-parser/FIELD_PROTOCOL.md). La primera evaluación se ejecutará sin ajustes y separará participantes completos; el producto sigue en `ITERATE` hasta observar evidencia técnica y de problema.

# Tecnología

Next.js/TypeScript PWA; Tailwind/shadcn; Supabase/PostgreSQL; almacenamiento temporal de audio; servicio STT intercambiable; extracción estructurada con JSON Schema; validadores TypeScript; consultas SQL para cifras; pruebas con fixtures de montos y unidades.

# Datos necesarios

Frases reales, diccionario de unidades/productos del segmento, operaciones de referencia, correcciones, ruido/contexto y métricas de uso. Audio se borra pronto salvo consentimiento separado para mejorar el sistema.

# Modelo comercial

B2B SaaS ligero o servicio asistido: piloto 7 días; prueba pagada USD 10–20/mes con onboarding; luego USD 3–8/mes si retención y costos lo permiten. Asociación como canal, no publicidad ni venta de datos.

# Riesgos

Errores monetarios silenciosos; baja confianza; ruido; conectividad; costo STT; nombres/deudas en audio; competencia de POS; soporte intensivo. Mitigación central: el modelo propone y el usuario confirma; los totales no los genera un LLM.

# Kill criteria

- <65% de operación completa aun restringiendo dominio.
- Corregir tarda igual o más que el método actual.
- Menos de 2 de 5 negocios siguen usando tras tres días.
- Cualquier error de monto guardado sin confirmación.
- Costo variable >20% del precio objetivo sin alternativa.
- La necesidad principal resulta ser facturación SRI, no registro rápido.

# Expansión futura

Otros mercados de Ecuador y Latinoamérica, idiomas/regiones adicionales, integración con proveedores contables y una capa RESCATA que use inventario próximo a perderse solo con autorización granular.
