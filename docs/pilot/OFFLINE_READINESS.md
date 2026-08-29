# Preparación futura para offline

**Gate actual:** `OFFLINE_HOLD`.

El motor determinista y SQLite pueden ejecutarse localmente, pero la interfaz desplegada depende de HTTPS, API remota, protección del proveedor y disponibilidad del volumen. Los tokens son efímeros y las propuestas viven en memoria del proceso.

## Bloqueos para offline real

- empaquetado local/PWA y service worker;
- cola durable con IDs idempotentes;
- sincronización y resolución de conflictos;
- cifrado local y revocación de dispositivo;
- migraciones offline;
- UX explícita de estado pendiente/sincronizado;
- prueba de doble escritura y recuperación.

No almacenar frases offline ni simular sincronización durante P01. Reabrir solo si conectividad real aparece como fricción repetida.
