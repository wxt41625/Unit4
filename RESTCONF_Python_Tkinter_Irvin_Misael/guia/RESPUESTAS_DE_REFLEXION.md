# Respuestas de reflexión y análisis — U4ACT02

**Alumno:** Irvin Misael Mejía Hernández  
**Equipo:** Cisco Catalyst 8000V (IOS XE)  
**Actividad:** RESTCONF con Python y Tkinter

## 1. ¿Cómo se convierten los datos de tk.Entry al diccionario yangConfig?

En la ventana, cada campo `tk.Entry` contiene un dato que capturó el usuario y que puede recuperarse con `.get()`. La función `_config()` recoge el nombre de la interfaz, la IP, la máscara y la descripción. Luego llama a `construir_yang_config(...)`, que comprueba el formato del nombre, valida la IP y la máscara con `ipaddress` y compone un diccionario de Python. Las claves del diccionario siguen el modelo YANG de `ietf-interfaces` e `ietf-ip`, por ejemplo `ietf-interfaces:interface`, `name`, `enabled` e `ietf-ip:ipv4`. El booleano se escribe `True` en Python, mientras que al convertirlo con `json.dumps(yangConfig)` queda como `true` en JSON. Finalmente, `requests.put()` o `requests.post()` envía ese JSON a IOS XE con `Content-type: application/yang-data+json` y Basic Auth.

**Recorrido del dato:** `tk.Entry` → `StringVar.get()` → validación (`ipaddress`) → `yangConfig` (diccionario) → `json.dumps()` → petición RESTCONF.

## 2. ¿Qué ventaja aportan eventos y callbacks en Tkinter frente a scripts lineales?

Un script lineal ejecuta sus acciones secuencialmente y termina. Con Tkinter, la ventana permanece disponible y espera eventos del usuario: pulsar **Consultar interfaz** ejecuta el callback `_consultar`; pulsar **Crear / actualizar (PUT)** ejecuta `_guardar_put`; y pulsar **Eliminar interfaz** muestra antes un `messagebox.askyesno()` de confirmación. Los callbacks permiten organizar acciones independientes, validar únicamente los campos necesarios y reaccionar al código HTTP. Además, las peticiones se ejecutan en un hilo secundario y sus resultados se llevan mediante una cola a la interfaz principal. Esto evita congelar la GUI mientras espera la respuesta HTTPS y permite actualizar el indicador verde/rojo al terminar.

## 3. Pregunta del PDF, parte 2, inciso y: ¿qué cambios se aplicaron para eliminar Loopback99?

Se conservó la URL de la interfaz específica (`.../ietf-interfaces:interfaces/interface=Loopback99`) y la autenticación Basic Auth, pero se reemplazó `requests.put(...)` por **`requests.delete(...)`**. Ya no es necesario enviar el diccionario `yangConfig` ni `data=json.dumps(...)`, porque DELETE solicita la eliminación del recurso identificado por la URL. Se comprobó el código HTTP de la respuesta; un resultado `2xx`, como `204 No Content`, indica éxito. La eliminación se verifica con `show ip interface brief` o intentando consultar Loopback99 con GET, que normalmente responderá 404 si ya no existe. El programa gráfico incorpora además una confirmación obligatoria antes de DELETE.

## 4. Interpretación de respuestas HTTP

- **200 OK:** consulta o cambio exitoso.
- **201 Created:** recurso creado.
- **204 No Content:** operación exitosa sin cuerpo de respuesta, habitual en DELETE.
- **401 Unauthorized:** credenciales de RESTCONF incorrectas.
- **404 Not Found:** recurso inexistente o ruta RESTCONF errónea.
- **500 Internal Server Error:** fallo del servicio o del dispositivo; se conserva el detalle que devuelve el router.

*Estos conceptos están respondidos a nivel de análisis. Los resultados reales y las capturas deben obtenerse tras ejecutar el laboratorio en el Catalyst 8000V conectado por OpenConnect.*
