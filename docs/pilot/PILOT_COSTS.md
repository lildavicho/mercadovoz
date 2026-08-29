# Costos del piloto — decisión de hosting actualizada 29-08-2026

| Componente | Opción | Costo publicado | Decisión |
|---|---|---:|---|
| Desarrollo local | Python/SQLite/Next.js | `$0` adicional | Usar |
| Hosting único | Oracle Cloud Ampere A1 Flex, 2 OCPU/12 GB/50 GB | `TO_VERIFY` en la cuenta/región antes de crear | Target actual |
| Boot volume/backups | OCI | `TO_VERIFY` | Configurar límites y retención |
| Observabilidad externa | no integrada | `TO_VERIFY` | No crear cuenta |
| ASR futuro | no autorizado | `TO_VERIFY` | `VOICE_HOLD` |
| LLM futuro | no autorizado | `TO_VERIFY` | `LLM_HOLD` |

Referencia técnica: [Oracle Arm-Based Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/References/arm.htm). La preparación anterior Vercel/Railway quedó supersedida por ADR-005 y no autoriza compras.

Los precios pueden cambiar. No se compró plan. Antes de activar P01, el usuario debe escoger una combinación permitida y configurar límites/avisos de gasto.
