# Preparación de Catalyst 8000V con OpenConnect

Alumno: **Irvin Misael Mejía Hernández**.

## 1. Conecta la VPN

Abre OpenConnect tal como te indicó tu profesor o el sandbox de Cisco. Si la conexión queda esperando una contraseña, desafío MFA o aprobación, soluciona primero la conexión VPN. **La VPN no sustituye las credenciales RESTCONF del router.** El servidor VPN y la IP del Catalyst 8000V pueden ser distintos.

En Linux puedes revisar la interfaz y ruta hacia el router (cambia `<IP_DEL_ROUTER>`):

```bash
ip -br addr
ip route get <IP_DEL_ROUTER>
ping -c 3 <IP_DEL_ROUTER>             # opcional: ICMP podría estar bloqueado
curl -k -I --max-time 10 https://<IP_DEL_ROUTER>:443/     # sirve para probar HTTPS
```

No supongas que `192.168.56.101` del PDF sea tu IP real: es solo el ejemplo del material.

## 2. Comprueba RESTCONF en el Catalyst

En la CLI del Catalyst 8000V, si tienes permiso para ver/configurar:

```text
enable
show version
show ip interface brief
show running-config | include restconf|ip http secure-server|ip http authentication
```

Si RESTCONF no está habilitado y **tienes autorización para cambiarlo**, Cisco documenta estos comandos para IOS XE:

```text
configure terminal
restconf
ip http secure-server
ip http authentication local
end
```

La línea `ip http authentication local` corresponde a usar las credenciales locales si ese es el esquema de autenticación del laboratorio. **No crees usuarios ni modifiques AAA si no cuentas con permiso del profesor**; si se usa un sandbox compartido, reutiliza el usuario autorizado que te proporcionaron.

## 3. Prueba HTTPS RESTCONF desde tu equipo Linux

El siguiente `curl` pregunta la contraseña de manera interactiva (no la escribas en el comando ni en capturas):

```bash
curl -k --max-time 15 -u TU_USUARIO \
  -H 'Accept: application/yang-data+json' \
  'https://<IP_DEL_ROUTER>/restconf/data/ietf-interfaces:interfaces'
```

Con `-k`, curl acepta un certificado TLS autofirmado. Eso es apropiado **solo en un sandbox/laboratorio de confianza**; en producción usa TLS validado.

## 4. Ejecuta y verifica

```bash
./INICIAR_LINUX.sh
# o después de preparar tu entorno virtual:
python3 app_tkinter.py
```

Llena IP/hostname, puerto 443, usuario y contraseña. Luego:

1. GET a `GigabitEthernet1` para demostrar lectura sin cambiar la configuración.
2. POST para crear `Loopback99` (si ya existe, evita repetir POST); captura HTTP 201 si el servidor lo devuelve.
3. GET a `Loopback99`; revisa IP 99.99.99.99, máscara 255.255.255.0 y estado habilitado.
4. PUT sobre `Loopback99`; muestra confirmación y guarda la respuesta. Puede ser HTTP 200, 201 o 204 según dispositivo/operación.
5. En CLI ejecuta `show ip interface brief` y, si está disponible, `show running-config interface Loopback99`.
6. Usa DELETE en la GUI, acepta `messagebox.askyesno` y verifica por GET/CLI que desapareció.
7. Guarda las evidencias reales y súbelas a tu rama de GitHub.

## 5. Diagnóstico rápido

| Síntoma | Posible causa | Acción |
|---|---|---|
| No conecta / timeout | VPN desconectada, IP incorrecta o ruta bloqueada | `ip route get`, prueba puerto 443, OpenConnect |
| HTTP 401 | Usuario o clave incorrecta | Usa credenciales autorizadas del Catalyst |
| HTTP 403 | Cuenta sin permisos | Verifica autorizaciones del sandbox |
| HTTP 404 | Interfaz no creada, nombre distinto, ruta RESTCONF incorrecta | GET de todas, verifica el nombre |
| HTTP 405/415 | Método o tipo de recurso no admitido | Comprueba la API YANG habilitada |
| HTTP 409 | Loopback ya creada o conflicto | Usa PUT para actualizar o elige una Loopback libre |
| HTTP 500 | Error del router/backend | Consulta respuesta JSON y logs del equipo |
| Error TLS | Certificado no confiable | Desmarca verificación SSL solo en sandbox |

**Fuentes de compatibilidad:**
- Cisco IOS XE 17.15 RESTCONF: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1715/b_1715_programmability_cg/restconf_protocol.html
- Cisco DevNet: Catalyst 8000V y ejemplo GET `ietf-interfaces`: https://developer.cisco.com/docs/modeling-labs/cat-8000v/
- Cisco IOS XE lab módulo 4 RESTCONF, POST YANG: https://github.com/jeremycohoe/cisco-ios-xe-programmability-lab-module-4-restconf
