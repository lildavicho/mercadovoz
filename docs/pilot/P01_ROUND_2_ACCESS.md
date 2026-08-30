# Acceso privado — P01 Round 2

**Estado:** rotado y preparado

**Ronda:** `P01_R2`

**Valores secretos en este documento:** ninguno

La credencial P01 y el token del operador se generaron en Oracle y no se imprimieron ni copiaron a Git. El registro de entrega local está en:

```text
/etc/mercadovoz/operator/p01-r2-access.json
```

Permisos: `0600 root:root`. Para recuperarlo desde una terminal autorizada del servidor:

```bash
sudo cat /etc/mercadovoz/operator/p01-r2-access.json
```

No pegar el resultado en chats, issues, documentación, historial de comandos compartido ni capturas. El código anterior y los tokens emitidos en R1 quedaron revocados. Rotar otra vez ante sospecha de exposición.
