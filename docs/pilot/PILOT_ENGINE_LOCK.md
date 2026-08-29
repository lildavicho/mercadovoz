# Congelamiento del motor — `pilot-v0-pre-field`

**Fecha:** 29 de agosto de 2026  
**Estado Git:** motor incorporado sin cambios funcionales al repositorio dedicado en el commit `32f2cfa` (`refactor: establish application and engine boundaries`). El remote se publica después de las auditorías de seguridad.  
**ENGINE_VERSION:** `1.0.0`  
**PARSER_VERSION:** `rules-v0.1.0+explicit-v0.3.0+context-v0.2.0+safety-v0.1.0`  
**SCHEMA_VERSION:** `operation-v0.1.0`  
**PILOT_VERSION:** `pilot-v0`  
**UI_VERSION:** `pilot-ui-v0`

## Verificación previa

- 47/47 pruebas Python en la estructura dedicada.
- TypeScript sin errores.
- Next.js production build correcto.
- Baseline v0: 8/8 hashes.
- Held-out independiente limpio: intent 11/11, campos 40/44, compuestos 3/3 y violaciones monetarias 0/4.
- Resultado reproducido: `research/benchmarks/results/pre-sprint3-repro.json`, SHA-256 `94dbc1b09c6325cb1cac8ec4a6ee8419852ed72eb9eb856a23af2e0fd82f720c`.

## Archivos congelados

```text
1bd7c9517db964f0f6d095b750ca6b3e4994c2cf1e13d809b1aafcdf9945d3a0  engine/src/mercadovoz_core/engine.py
199007ed9fead74581dcfd91d492b276a8af96c7eb1bd59eb8ee749c63731353  engine/src/mercadovoz_core/parsers.py
d3622cda1f2bc0a09b3419b4fe7dd4c4dc36d84f9d28c32a0e9d240cd5971940  engine/src/mercadovoz_core/safety.py
da03a26eaae07cf7bd036994e5507ceb199516398307de8ecd501b57765eb413  engine/src/mercadovoz_core/context.py
149316eb1a44523f05340ec899dd4bdaafe5514ecace4bf24adfcb6ebb353986  engine/src/mercadovoz_core/explicit_rules.py
4cb0f7118892b46b58c3607ce98add4e8a81e4e06ef604d80a925e23423357a7  engine/src/mercadovoz_core/corrections.py
c45ae170e795b736f0385164c5adce5d6c5ade51f22e133fcefdb5d6ce2c437e  engine/src/mercadovoz_core/versioning.py
26d473c39de349c1be01d636480c64d2608fea01b30054e4fce9282bae017d23  engine/schemas/operation.schema.json
```

## Regla durante P01 Round 1

No modificar reglas, parser, safety, contexto, normalización, extracción, clasificación ni correcciones. Los fallos se registran y se analizan después de cerrar la ronda. Cualquier cambio posterior exige nueva versión de engine, nuevo lock y comparación explícita; nunca sobrescribe `pilot-v0`.
