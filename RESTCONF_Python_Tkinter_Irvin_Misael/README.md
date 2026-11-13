# U4ACT02 — RESTCONF con Python y Tkinter

**Alumno:** Irvin Misael Mejía Hernández  
**Router:** Cisco Catalyst 8000V (IOS XE 16.6 o posterior)  
**Conexión:** OpenConnect VPN + HTTPS/RESTCONF (443)  
**Rama solicitada:** `feat/unidad4_act02`

Esta carpeta implementa el laboratorio de seis páginas **U4ACT02 RESTCONF with Python**, incluyendo Partes 1 y 2, los desafíos de los niveles 1-3 de Tkinter y materiales para la entrega de GitHub. Las credenciales y la IP reales **no se conocen**: se introducen en la interfaz o se solicitan por consola, sin guardarlas en los archivos.

## Arranque rápido en Debian/antiX

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip python3-tk
cd RESTCONF_Python_Tkinter_Irvin_Misael
./INICIAR_LINUX.sh
```

También puedes iniciar con:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app_tkinter.py
```

En otro Linux con Python >= 3.10, instala Tkinter mediante el gestor de paquetes de tu distribución y luego `requests` dentro de un virtualenv.

**No cierres OpenConnect durante las pruebas.** En la sección de conexión de la GUI introduce la IP de gestión del router, puerto (normalmente 443), usuario y contraseña RESTCONF. La casilla para verificar TLS está desmarcada por defecto solamente para permitir certificados autofirmados del entorno educativo.

## Qué hace la GUI

- **1. Consultar (GET):** campo `tk.Entry` para nombre; botón `tk.Button` para consultar; `ttk.Treeview` con interfaz, IPv4, máscara, estado administrativo y descripción. También lista todas las interfaces.
- **2. Crear / actualizar (POST / PUT):** formulario para Loopback, IP, máscara y descripción. Construye `yangConfig` dinámico y lo serializa con JSON; muestra ventana de éxito cuando el HTTP es 2xx.
- **3. Eliminar (DELETE):** solicita confirmación `messagebox.askyesno` antes de borrar LoopbackN.
- **UX:** barra inferior verde al lograr 2xx, roja ante HTTP 401, 404, 500 y demás errores. La petición corre en un hilo separado para no bloquear la GUI.

Para evitar perder conexión a la VPN, las modificaciones y borrados solamente permiten nombres `LoopbackN`. Las consultas GET también admiten nombres como `GigabitEthernet1`.

## Scripts CLI que corresponden al PDF

| Archivo | Parte del laboratorio | Qué ejecutar |
|---|---|---|
| `lab 2.5.py` | Parte 1, GET / JSON legible | `python3 'lab 2.5.py'` |
| `lab 2.5 part2.py` | Parte 2, PUT Loopback99 | `python3 'lab 2.5 part2.py'` |
| `lab 2.5 eliminar.py` | Incisos x, y: cambiar PUT por DELETE | `python3 'lab 2.5 eliminar.py'` |
| `lab 2.5 post.py` | Complemento del desafío POST | `python3 'lab 2.5 post.py'` |

Cada script imprime el nombre completo del alumno, pide IP/usuario y oculta la contraseña con `getpass`. Admite, opcionalmente, variables de entorno `RESTCONF_HOST`, `RESTCONF_PORT`, `RESTCONF_USER`, `RESTCONF_PASSWORD`; evita guardar claves en archivos o historial de comandos.

## Pruebas sin tocar el router

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Las pruebas simulan respuestas GET/POST/PUT/DELETE y errores 401, 404, 500 y timeout; no abren conexiones de red. **Pasar estas pruebas no significa haber probado un Catalyst real.**

## Estructura del proyecto

```text
RESTCONF_Python_Tkinter_Irvin_Misael/
├── app_tkinter.py                 GUI completa Tkinter
├── restconf_cliente.py            Cliente RESTCONF, YANG y validaciones
├── cli_comun.py                   Entrada segura de IP/usuario/clave para CLI
├── lab 2.5.py                     GET original del PDF, adaptado a tu router
├── lab 2.5 part2.py               PUT Loopback99 del PDF
├── lab 2.5 eliminar.py            DELETE Loopback99, inciso x/y
├── lab 2.5 post.py                POST complementario
├── INICIAR_LINUX.sh               Arranque Linux + entorno virtual
├── requirements.txt               Dependencia requests
├── tests/test_restconf.py         Pruebas locales
├── guia/CATALYST_8000V_OPENCONNECT.md
├── guia/RESPUESTAS_DE_REFLEXION.md
├── guia/CHECKLIST_EVALUACION.md
├── guia/GITHUB_Y_PULL_REQUEST.md
├── .github/PULL_REQUEST_BODY.md
├── evidencias/README.md           Lista de capturas reales pendientes
└── material_original/             Copia del PDF recibido
```

## Qué queda necesariamente pendiente

1. Conectar OpenConnect e introducir **IP de administración, usuario y contraseña reales** del Catalyst 8000V; estos datos no vienen determinados por el PDF.
2. Ejecutar operaciones contra ese router y registrar capturas auténticas de respuestas (además de la ventana de Tkinter).
3. Enviar el código y evidencias al repositorio, crear el PR de `feat/unidad4_act02` y registrar su captura. Sin enlace/permisos del repositorio, un ZIP no puede crear el PR.

Lee `guia/CATALYST_8000V_OPENCONNECT.md` para configuraciones IOS XE y `guia/CHECKLIST_EVALUACION.md` para la lista de evidencias exigidas. **No se incluyen contraseñas ni se afirma que haya conexión a un router real.**
