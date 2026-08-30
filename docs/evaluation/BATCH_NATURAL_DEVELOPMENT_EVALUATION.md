# Evaluación batch natural de desarrollo

**Corpus:** `MANUAL_NATURAL_BATCH_DEVELOPMENT`, 100 narrativas únicas, 260 operaciones esperadas y 123 campos anotados. Incluye longitudes de 2, 3, 5, 8 y 10+ movimientos, ruido, muletillas, autocorrección, incertidumbre, varios clientes, deudas, grupos y éxito parcial. No es evidencia humana ni held-out.

| Métrica | Engine 1.2 |
|---|---:|
| Segment count exacto | 82,00% |
| Boundary precision / recall | 89,53% / 92,98% |
| Intent por ítem | 91,92% |
| Campos anotados | 96,75% |
| Batch exact match | 76,00% |
| Safe partial recovery | 92,31% |
| Unsafe merge rate | 0,70% (merges no confirmables) |
| Source-span integrity | 100% |
| Amount crossover / customer crossover | 0 / 0 |
| Violaciones financieras críticas | 0 |

El benchmark web-derived congelado mejoró de 29,17% a 30,00% en recall de operaciones y de 37,20% a 39,63% en campos; batch exact pasó de 11,67% a 13,33%, con cero violaciones. Sigue siendo débil porque sus pares no son narrativas naturales y contienen operaciones fuera del alcance core.

El corpus sintético permanece separado: 3.000 narrativas, 24.000 operaciones, 100% en invariantes anotados y cero violaciones. No se usa para ocultar la brecha externa.

**Gate:** `BATCH_NATURAL_DEVELOPMENT_EVALUATED`. La seguridad permite conservar el candidato, pero `BATCH_GENERALIZATION_HOLD` continúa hasta obtener batch natural independiente/real; la bandera permanece apagada en P01_R3.
