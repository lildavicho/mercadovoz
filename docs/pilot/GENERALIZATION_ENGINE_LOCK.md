# Lock del candidato de generalización

**Fecha:** 30 de agosto de 2026  
**Commit de código:** `0432d369c85c12ef7bd9d21a88ce1ed148478d0d`  
**ENGINE_VERSION:** `1.1.0`  
**PARSER_VERSION:** `rules-v0.1.0+explicit-v0.4.0+context-v0.2.0+safety-v0.2.0`  
**SCHEMA_VERSION:** `operation-v0.1.0`

Este lock describe el candidato local posterior a P01/manual development. No reemplaza ni modifica [`PILOT_ENGINE_LOCK.md`](PILOT_ENGINE_LOCK.md), que conserva la ronda desplegada con `engine 1.0.0`. `1.1.0` no debe desplegarse sobre una ronda activa.

## Hashes SHA-256

| Archivo | SHA-256 |
|---|---|
| `engine/src/mercadovoz/parser.py` | `f3d2ab4cb119fb508a34e9cb0f8b16a797905bf0aecf137dfc840cf8ee2284d8` |
| `engine/src/mercadovoz/numbers.py` | `7325879190f905b980cfa1e8bac6320fe810d3a1a2436f2e6836e71c6ed6e7f9` |
| `engine/src/mercadovoz_core/explicit_rules.py` | `bb209dd43fb29a084c4e325839340193aad9da6b7cb0354a733df182039ad751` |
| `engine/src/mercadovoz_core/safety.py` | `2097e26f4e2a5abeeb31fb3ae6546eadbc70fe3ac6901585fed6c37998eb6097` |
| `engine/src/mercadovoz_core/engine.py` | `f9f412c1707d5fd7cfbe7dce5296bce6ec0d6cba540694fac35d5422a8251d14` |
| `engine/src/mercadovoz_core/corrections.py` | `d71e5cd60a69c059d4073249caee72ddbfd1eb8008ab478069c463d082127c07` |
| `engine/src/mercadovoz_core/workflow.py` | `a59a8b9321cc6f072b44dea78cd3ed802b25f30b1c6a07b89196c8931ee17a46` |

## Evidencia de cierre local

- Python: 60 pruebas (incluye cinco regresiones manuales, invariantes y 3.600 variantes deterministas).
- Frontend: 3 pruebas de idempotencia HTTP/HTTPS.
- Externo independiente limpio: 11/11 intención, 40/44 campos, 3/3 compuestos, 0/4 violaciones críticas.
- Externo completo: 69/85 intención, 199/290 campos, 25/25 compuestos, 0/67 violaciones críticas.
- Sintético de evaluación: 22/30 estado, 58/80 campos, 0 propuestas inseguras.

Los resultados completos se generan en `data/runtime/` y no se versionan. Antes de abrir una nueva ronda, recalcular estos hashes desde el commit final de release y registrar cualquier diferencia.
