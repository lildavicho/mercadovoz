# Modelo de privacidad — `pilot-v0`

## Propósito y clases

| Clase | Datos mínimos | Propósito |
|---|---|---|
| `OPERATIONAL_DATA` | operación confirmada, alias, saldo, timestamps | cuaderno e historial |
| `EVALUATION_DATA` | texto original, predicción, correcciones, outcome | medir interpretación y UX |
| `AUDIT_DATA` | eventos relevantes y versiones | reconstruir decisiones/errores |
| `ANALYTICS_DATA` | métricas agregadas y latencias | evaluar el gate |

## Recolectado

ID pseudónimo, sesión, consentimiento, texto escrito, normalización separada, propuesta, campos, faltantes, contexto, advertencias, safety events, correcciones estructuradas, resultado humano y latencias. El alias que la persona escriba puede permanecer como referencia operativa.

## No recolectado intencionalmente

Nombre completo del participante, cédula, teléfono, correo, dirección, cuenta bancaria, fotografía, audio, ubicación precisa, IP almacenada, fingerprint o contactos. La UI no solicita datos de identidad de clientes/deudores.

## Acceso y separación

- Cada participante solo consulta operaciones, deudas y auditoría asociadas a su token/sesión.
- El operador usa un token separado para métricas/anotaciones y herramientas locales para exportar/eliminar.
- Un eventual mapa `P01 → identidad` debe vivir fuera de la base, exports y repositorio.
- `REAL_DEVELOPMENT`, `REAL_HELDOUT`, `WEB_DERIVED`, `WEB_DERIVED_MULTISOURCE` y `SYNTHETIC` nunca se mezclan.

## Retención y eliminación

- Piloto activo: conservar datos operativos/evaluación hasta 90 días después del cierre de la ronda.
- Antes del día 90: exportar y congelar la versión necesaria o eliminarla.
- Solicitud de retiro: eliminar participante o sesión desde herramienta de operador; conservar un registro externo mínimo de que la solicitud fue atendida, sin texto financiero.
- Los backups siguen su retención técnica; no se promete borrado inmediato de copias ya creadas.

## Exportación y pseudonimización

Exports privados JSONL/CSV omiten tokens, códigos, headers, IP y configuración. El export de evaluación mantiene `participant_id` pseudónimo porque el split futuro es por persona.

## Incidentes

Detener acceso, preservar logs sin difundir texto, rotar secretos, identificar sesiones afectadas, evaluar eliminación/restauración y documentar decisiones. Avisos legales o a participantes requieren revisión humana según el caso.

## Límites

SQLite no cifra por sí mismo el archivo; se depende de controles y cifrado del proveedor. No se declaran certificaciones ni cumplimiento jurídico no verificado.
