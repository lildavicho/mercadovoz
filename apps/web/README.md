# MercadoVoz — interfaz de piloto privado

Flujo móvil: `ESCRIBIR → ENTENDÍ ESTO → CONFIRMAR / CORREGIR / RECHAZAR / CANCELAR → GUARDADO`.

## Desarrollo local

Backend, desde la raíz:

```powershell
$env:MERCADOVOZ_ENV='pilot'
$env:MERCADOVOZ_DB='.\pilot-local.db'
$env:MERCADOVOZ_PILOT_ACCESS_CODES='{"P01":"código-local-no-reutilizable"}'
$env:MERCADOVOZ_OPERATOR_TOKEN='token-local-no-reutilizable'
$env:MERCADOVOZ_ALLOWED_ORIGINS='http://localhost:3000'
python -m uvicorn mercadovoz_core.service:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
Set-Location apps\web
$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8000'
npm run dev
```

Los valores son ejemplos locales, no secretos de campo. No guardar la DB resultante como evidencia real.

## Producción privada

El frontend solo necesita `NEXT_PUBLIC_API_URL`. No colocar códigos, tokens ni DB URL en variables `NEXT_PUBLIC_*`. Vercel se configura desde esta carpeta; la API/SQLite corre por separado en un servicio singleton con volumen.

## Límites

Sin voz, LLM, inventario completo, SRI, multiempresa, marketing ni precision humana afirmada. Refrescar o cerrar elimina el token del navegador y requiere nueva invitación.
