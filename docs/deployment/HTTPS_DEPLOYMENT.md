# HTTPS del piloto privado

**Hostname:** `129-80-183-35.sslip.io`

**Destino DNS verificado:** `129.80.183.35`

**Certificado:** Let's Encrypt ECDSA

**Vigencia inicial:** 30 de agosto a 28 de noviembre de 2026

**SHA-256 fingerprint:** `76:7A:44:FE:38:C7:02:A6:31:C4:7D:97:6B:E1:8F:55:A4:F2:33:58:23:13:2E:5D:3A:9B:7A:FA:7E:D0:D0:6F`

## Configuración verificada

- Nginx escucha 80/443; 3000/8000 permanecen en loopback.
- HTTP redirige permanentemente al hostname HTTPS.
- Certbot instaló el certificado con el plugin Nginx.
- `certbot.timer` está activo.
- La renovación simulada completa pasa.
- La API usa el origin exacto HTTPS y la web usa same-origin.
- La configuración previa de Nginx quedó respaldada como `/etc/nginx/sites-available/mercadovoz.before-20260830-p01-r2-https`.

## Renovación y chequeo

```bash
sudo certbot certificates
sudo certbot renew --dry-run --no-random-sleep-on-renew
sudo nginx -t
systemctl is-active nginx certbot.timer
```

El hostname gratuito evita comprar un dominio para P01, pero su DNS es una dependencia externa. Si cambia la IP, el nombre deja de apuntar a la instancia. Para ampliar el piloto, migrar a un dominio controlado y emitir otro certificado sin reusar secretos.
