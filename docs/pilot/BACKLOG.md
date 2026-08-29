# Backlog priorizado

## Completado — benchmark externo y núcleo

- [x] Ingerir sin transformación los cuatro archivos de `external-cuenca-v1` y registrar hashes.
- [x] Ejecutar v0 y v1 iniciales antes de ajustar reglas.
- [x] Congelar development/held-out por familias y registrar fuga estructural.
- [x] Separar 42 casos con artefactos de calidad sin corregir etiquetas ni aprenderlos.
- [x] Completar dos iteraciones generales usando solo development.
- [x] Pasar el gate técnico en held-out independiente limpio.
- [x] Mantener 8/8 hashes del baseline v0.
- [x] Implementar dominio, parsers versionados, correcciones controladas, confirmación idempotente y auditoría.
- [x] Implementar API local y persistencia SQLite mínima.
- [x] Implementar Text MVP móvil con propuesta, corrección, confirmar/cancelar, historial y cuentas por cobrar.
- [x] Verificar 40 pruebas, tipos, build y navegador móvil/escritorio.

## Completado — Sprint 3 preparación privada

- [x] Congelar motor/versiones/hashes antes de uso real.
- [x] Implementar acceso por invitación, consentimiento, sesiones y aislamiento.
- [x] Persistir eventos, correcciones estructuradas y outcome humano.
- [x] Confirmar operación + auditoría en una transacción e integrar idempotencia.
- [x] Añadir métricas congeladas, export JSONL/CSV, anotación y eliminación.
- [x] Adaptar UX móvil privada con historial/audit y cierre/feedback.
- [x] Auditar secretos, rutas dev, headers, dependencias y logs.
- [x] Preparar Vercel + Railway/volumen, rollback, backups y protocolo V2.
- [x] Verificar 47 pruebas, tipos, build y E2E móvil/escritorio.

## Próximo gate — acción externa y evidencia humana

- [ ] Conectar despliegue privado, volumen y secretos; completar restore drill.
- [ ] Ejecutar prueba sintética remota y eliminarla antes de P01.
- [ ] Iniciar P01 solo tras consentimiento real.

- [ ] Capturar P01 real con consentimiento y guardar primero `data/private/p01-baseline-v0.json`.
- [ ] Recolectar 50–100 frases de 6–8 participantes y congelar participantes completos para held-out.
- [ ] Medir tiempo de tarea, turnos de corrección, abandono y operación equivocada confirmada.
- [ ] Comparar el flujo con el cuaderno o memoria que cada participante usa hoy.
- [ ] Decidir `FIELD_VALIDATION_GO / REDUCE_SCOPE / KILL` sin usar el corpus web como sustituto.

## Después de P01 Round 1

- [ ] Exportar y congelar `REAL_DEVELOPMENT` con hashes.
- [ ] Completar reporte/taxonomía y emitir gate de iteración.
- [ ] Corregir únicamente causas generales en engine nueva y comparar Round 2.

## Solo después de gates de campo

- [ ] Evaluar PWA y autenticación si el piloto realmente las exige.
- [ ] Probar ASR separado de texto→operación con audio consentido.
- [ ] Comparar híbrido o LLM structured output solo si el lenguaje real supera las reglas.
- [ ] Diseñar cierre diario o exportación cuando el comportamiento observado lo justifique.

## No hacer todavía

- dashboard grande, ERP, facturación/SRI, inventario completo o SaaS multiempresa;
- múltiples operaciones automáticas, `PAYABLE` o retiro/aporte como operaciones core;
- promesas de accuracy, landing pública, marketing o contacto con terceros;
- repositorio nuevo, push o publicación.

Una tarea entra únicamente si reduce un riesgo observado o desbloquea el siguiente gate con un criterio medible.
