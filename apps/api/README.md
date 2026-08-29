# MercadoVoz API

Entrada FastAPI del piloto privado. La aplicación importa el motor versionado desde `engine/`; no contiene reglas de interpretación propias.

Desde la raíz:

```powershell
python -m pip install -e ".[api]"
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

En `MERCADOVOZ_ENV=pilot` se requieren las variables descritas en `.env.example`. Las rutas de laboratorio, OpenAPI y documentación interactiva quedan desactivadas.
