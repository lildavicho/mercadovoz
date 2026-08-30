# Decisión de STT para MercadoVoz — 30 de agosto de 2026

## Decisión

No conectar todavía un proveedor real. Mantener `SpeechTranscriber` con mock y un adaptador Web Speech solo para laboratorio. Para un benchmark autorizado, evaluar primero Azure Speech en `brazilsouth` con locale `es-EC`, y comparar contra Google Cloud STT y OpenAI `gpt-transcribe`. Es una hipótesis de selección, no evidencia de precisión en comerciantes de Cuenca.

## Comparación oficial

| Opción | Ecuador / streaming | Privacidad y región | Costo actual | Uso propuesto |
|---|---|---|---|---|
| Web Speech API | BCP-47 desde navegador; implementación/proveedor dependen del navegador | Retención y ubicación no quedan definidas por la especificación | Sin API contratada | Solo smoke test UX |
| Azure Speech | [`es-EC`](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support) y tiempo real; [`brazilsouth`](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions) soporta tiempo real | En tiempo real procesa en memoria y no almacena en reposo según [privacidad oficial](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/speech-service/speech-to-text/data-privacy-security) | F0/estándar: `TO_VERIFY` en la cuenta y región | Primera prueba controlada |
| Google Cloud STT V2 | [`es-EC`](https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages), actualmente asociado a `telephony_short`; streaming backend | Sync/stream procesa en memoria; async conserva resultado alrededor de 5 días; procesamiento regional único no soportado según [FAQ](https://docs.cloud.google.com/speech-to-text/docs/v1/data-usage-faq) | `TO_VERIFY` antes de crear proyecto | Comparador por locale |
| OpenAI `gpt-transcribe` | Multilingüe, archivo/streaming y pistas de vocabulario | API no se conecta hasta revisar controles y elegibilidad de retención en [documentación de datos](https://developers.openai.com/api/docs/guides/your-data) | [USD 0,0045/min](https://developers.openai.com/api/docs/models/gpt-transcribe) consultado el 30-08-2026 | Comparador de calidad/costo |
| AWS Transcribe | La [tabla oficial](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html) lista variantes españolas, pero no `es-EC` | Por defecto puede usar entradas para mejorar el servicio salvo [opt-out](https://docs.aws.amazon.com/es_es/transcribe/latest/dg/opt-out.html) | `TO_VERIFY` | No prioritario |
| Whisper / faster-whisper local | Multilingüe, no locale ecuatoriano contractual | Audio puede permanecer local; requiere medir hardware y empaquetado | Infraestructura `TO_VERIFY` | Comparador offline futuro |

## Criterios del benchmark

Exactitud de token monetario, sustitución crítica de dígitos, omisiones/inserciones, normalización, latencia mediana/p95, costo por minuto, funcionamiento móvil, residencia/retención y tasa de corrección humana. La muestra debe incluir habla ecuatoriana real consentida y ruido de mercado; ningún proveedor tiene hoy esa evidencia dentro del repositorio.

## Reversibilidad

La interfaz de transcripción permite cambiar proveedor sin modificar el parser, ledger o confirmación. No se han creado cuentas, enviado audio, comprado planes ni almacenado credenciales.
