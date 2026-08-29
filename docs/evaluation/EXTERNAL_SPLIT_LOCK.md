# Congelamiento — external dev/heldout v1

**Fecha:** 29 de agosto de 2026  
**Corpus padre:** `external-cuenca-v1`  
**Objetivo:** 75% development / 25% heldout sin separar innecesariamente familias estructurales

## Resultado

| Partición | Registros | Porcentaje |
|---|---:|---:|
| `external-dev-v1` | 182 | 75,83% |
| `external-heldout-v1` | 58 | 24,17% |
| Total | 240 | 100% |

La unidad de asignación es `phenomenon + source_id + structural_skeleton`. El skeleton normaliza mayúsculas, tildes, puntuación, números y placeholders; además sustituye valores gold de producto, cliente, categoría y unidad. Los grupos se ordenan determinísticamente mediante SHA-256 con seed `external-cuenca-v1-family-split`. Solo se añaden grupos completos cuando acercan el estrato al 25%.

Esto prioriza familias completas y separación por fuente. Si un fenómeno tiene un único grupo sobredimensionado que no puede entrar sin empeorar fuertemente la proporción, queda en development y se registra como limitación. Por eso `BUSINESS_EXPENSE`, `OWNER_CONTRIBUTION_SCHEMA_GAP` y `OWNER_WITHDRAWAL_SCHEMA_GAP` no aparecen en heldout v1.

## Archivos congelados

```text
2c636bf29551e6f356e730c3520e8d19bbf7b65a29d32b82555de8c7cfce6f18  external-dev-v1.ids.txt
05bdf5c3882045c1672fb988f1e0372b0c6d66b23b8f5911365b1e3ae5a2cffe  external-heldout-v1.ids.txt
99dc6140a7ccb5343d19df8f4640abb400e9b2142a52268720f61c594832bf66  external-leakage-risk-v1.ids.txt
e68e69e0d28395927c1a3e48a8bb17c6f12675a0bf3649f48de2e52083f94794  external-leakage-v1.json
4e5c94a6cbcac69b4afb48c708b97ec81c32c3dba258bddd67d02eb6bb32c609  external-split-v1.json
```

Los archivos están en [`research/external-cuenca-v1/manifests/`](../../research/external-cuenca-v1/manifests/). No se regenerarán para favorecer métricas. Cambiar algoritmo o seed exige `external-split-v2`.

## Corte de calidad

Cuarenta y dos registros contienen plurales generados de forma artificial (`unidads` o `pars`). Se conservan en el corpus y en el resultado completo, pero se excluyen del corte limpio para no premiar reglas dirigidas a errores del generador.

```text
aa7be1e3fb79117b485f7135c11a9f82d9d9b10a02886280fd81aada8b62d0cb  external-data-quality-risk-v1.ids.txt
b596501080d57d0c04de8b4f91e9c61d243bfee163709cdd004eb4f88f5610c4  external-independent-exclusions-v1.ids.txt
```

El segundo archivo combina exclusiones por fuga y calidad. Siete casos de calidad estaban en el held-out independiente: 36 independientes − 7 de calidad = 29 en el corte independiente limpio.

## Anti-leakage y conjunto independiente

Setenta y cinco registros externos comparten un skeleton exacto con P00-WEB o P01-WEB-DERIVED. Veintidós caen en heldout y se excluyen de cualquier afirmación de generalización independiente.

| Conjunto | Registros |
|---|---:|
| heldout congelado total | 58 |
| `LEAKAGE_RISK` dentro de heldout | 22 |
| heldout independiente elegible | 36 |

El heldout independiente cubre diez fenómenos, pero no es representativo de todo el corpus ni evidencia humana. Los casos excluidos siguen sirviendo como regresiones conocidas.

## Política de uso

- Development puede orientar hasta tres iteraciones generales.
- No se inspeccionan predicciones por caso del heldout para ajustar reglas.
- La decisión final usa primero heldout independiente, después seguridad conocida en el corpus completo y finalmente development.
- Ninguna partición cambia `FIELD_VALIDATION_STATUS = PENDING_REAL_DATA`.
