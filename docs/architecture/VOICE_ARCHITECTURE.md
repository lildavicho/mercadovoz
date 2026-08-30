# Arquitectura de voz experimental

## Estado

`VOICE_PROTOTYPE_HOLD`: existe una abstracción y UX de revisión detrás de `NEXT_PUBLIC_VOICE_EXPERIMENT=false`, pero no se ha validado micrófono físico, exactitud `es-EC`, ruido de mercado ni tratamiento contractual con un proveedor. No está desplegada ni habilitada en P01_R2.

## Pipeline obligatorio

```text
micrófono -> transcriber -> transcripción visible y editable
          -> aceptación humana -> Engine 1.2
          -> tarjetas por movimiento -> confirmación explícita -> persistencia
```

`SpeechTranscriber` separa captura del proveedor. El adaptador de laboratorio usa Web Speech y declara `es-EC`; el adaptador mock permite pruebas deterministas sin audio. Ningún adaptador puede confirmar o modificar saldos.

## Privacidad y retención

- La aplicación no crea archivos de audio ni incluye audio en el dataset.
- Cancelar descarta la transcripción en memoria del componente.
- Una transcripción aceptada se trata como texto financiero y conserva `input_mode=VOICE_TRANSCRIPT`.
- La política del servicio real debe revisarse antes de conectarlo; la aplicación no puede garantizar qué hace el navegador con Web Speech.
- Entrenamiento, almacenamiento de audio y reutilización requieren consentimiento separado.

## Riesgo monetario

Toda transcripción con dígitos, moneda o palabras numéricas muestra una advertencia. El benchmark futuro debe medir sustituciones (`15/50`, `16/60`, `13/30`, `14/40`, `17/70`, `18/80`, `19/90`), decimales (`5.50/55`), omisiones, inserciones, cantidad/precio invertidos y aproximaciones. Confianza del ASR nunca equivale a autorización financiera.

## Gate

Para `VOICE_PROTOTYPE_GO`: probar micrófono real en navegador soportado, transcripción visible/editable, cancelación, permisos, números/dinero y cero autoguardado. Para uso con participantes se exige además cerrar P01_R2, autorizar proveedor y actualizar consentimiento si cambia el tratamiento.
