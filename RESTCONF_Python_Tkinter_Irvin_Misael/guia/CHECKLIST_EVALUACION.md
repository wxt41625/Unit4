# Lista de cotejo para verificar antes de entregar

| Criterio del PDF | Evidencia preparada en el proyecto | Pendiente con router/GitHub |
|---|---|---|
| Ventana Tkinter, requests, json, ttk, advertencias SSL | `app_tkinter.py`, `restconf_cliente.py` | Captura de GUI |
| Basic Auth y headers `application/yang-data+json` | `restconf_cliente.py`, scripts `lab 2.5*.py` | Captura de GET exitoso |
| GET y visualización de IP, máscara y estado | Pestaña **Consultar (GET)** y `ttk.Treeview` | Captura de información real |
| Formulario POST/PUT, `yangConfig` dinámico, mensaje de éxito | Pestaña **Crear / actualizar**, `construir_yang_config()` | Captura HTTP 201/200 y CLI |
| DELETE con confirmación `messagebox.askyesno()` | Pestaña **Eliminar (DELETE)** | Captura del diálogo y respuesta |
| Barra verde/roja, errores 401/404/500, try-except, GUI responsiva | `app_tkinter.py` con `threading` y `queue` | Capturas de éxito/error |
| Reflexión sobre `tk.Entry` hacia JSON | `guia/RESPUESTAS_DE_REFLEXION.md` | Completo (respuesta redactada) |
| Reflexión sobre eventos y callbacks | `guia/RESPUESTAS_DE_REFLEXION.md` | Completo (respuesta redactada) |
| GitHub `feat/unidad4_act02` | `guia/GITHUB_Y_PULL_REQUEST.md`, `.github/PULL_REQUEST_BODY.md` | Subir a tu repositorio y abrir PR real |
| `.py` ejecutable y capturas GUI | `app_tkinter.py`, `INICIAR_LINUX.sh`, `evidencias/` | Añadir evidencias reales al repositorio |
| PR con título/descripción | `.github/PULL_REQUEST_BODY.md` | Crear PR y capturar pantalla |

## Orden de evidencias sugeridas

1. `01_vpn_openconnect.png`: conectividad VPN activada (oculta datos privados).
2. `02_cli_restconf_activo.png`: RESTCONF habilitado y `show ip interface brief`.
3. `03_gui_get_gigabitethernet1.png`: GET en una interfaz física (solo lectura).
4. `04_gui_post_201.png`: POST de Loopback99 (201 Created), si lo permite el router.
5. `05_cli_show_loopback99.png`: nueva loopback visible en CLI.
6. `06_gui_get_loopback99.png`: GET con IP, máscara y estado en `Treeview`.
7. `07_gui_put_200.png`: PUT para actualizar Loopback99 (200/204 según equipo).
8. `08_gui_confirmacion_delete.png`: ventana de confirmación antes de DELETE.
9. `09_gui_delete_exitoso.png`: mensaje HTTP `2xx` de eliminación.
10. `10_gui_error_404.png`: GET de Loopback99 tras borrarla, barra roja.
11. `11_github_rama.png`: rama `feat/unidad4_act02`.
12. `12_github_pull_request.png`: PR con título y descripción.

**Importante:** no se incluyen capturas falsas. Las imágenes reales se añaden al terminar pruebas en tu Catalyst 8000V y GitHub.
