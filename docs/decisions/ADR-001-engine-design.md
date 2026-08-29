# ADR-001 — Stack del Text MVP

**Estado:** aceptado  
**Fecha:** 29 de agosto de 2026

## Decisión

Mantener el motor en Python y exponerlo mediante FastAPI; construir la interfaz con Next.js, React, TypeScript y Tailwind. Persistir localmente con SQLite.

## Motivo

- Portar reglas y seguridad a TypeScript duplicaría dos implementaciones antes de validar el producto.
- FastAPI conserva la API interna `interpret → propose → correct/confirm/reject` y permite probarla sin acoplarla a la UI.
- SQLite entrega historial y saldos básicos sin infraestructura externa ni servicio pagado.
- Next.js permite un flujo móvil claro y deja abierta una PWA posterior, pero no implica despliegue ni voz.

## Límites

- Una sola instancia local, sin autenticación ni multiempresa.
- Estado de propuestas en memoria; operaciones confirmadas y saldos sí persisten.
- CORS limitado a puertos locales de desarrollo.
- No shadcn/ui en esta primera pantalla: los pocos controles se mantienen propios y tipados; se reconsidera cuando existan dos patrones consumidores.
- No ASR, analytics, facturación, stock core ni publicación.
