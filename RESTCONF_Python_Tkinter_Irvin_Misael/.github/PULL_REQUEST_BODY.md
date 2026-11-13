# U4ACT02: Cliente RESTCONF con Python y Tkinter

**Alumno:** Irvin Misael Mejía Hernández  
**Dispositivo de laboratorio:** Cisco Catalyst 8000V, IOS XE  
**Conectividad:** OpenConnect (VPN)

## Resumen

Desarrollo de un cliente RESTCONF para interfaces IOS XE utilizando una GUI de Tkinter, peticiones HTTPS con Basic Auth y encabezados `application/yang-data+json`.

## Funcionalidad desarrollada

- Consulta GET de una interfaz o todas, con información ordenada en `ttk.Treeview`.
- Formulario para nombre, IP, máscara y descripción; validación de datos y construcción automática de `yangConfig`.
- Creación con POST y creación/actualización con PUT sobre LoopbackN.
- DELETE con confirmación visual `messagebox.askyesno()`.
- Indicador verde en respuestas HTTP 2xx; rojo para 401, 404, 500 u otros errores.
- Peticiones en hilo secundario para no bloquear la ventana.
- Scripts independientes del laboratorio (`lab 2.5.py`, `lab 2.5 part2.py`, `lab 2.5 eliminar.py`) y pruebas unitarias.
- Preguntas de reflexión y guía de configuración, conectividad y evidencias.

## Evidencias

Agregar aquí rutas o vistas de capturas REALES después de probar el dispositivo:

- [ ] GET desde la interfaz Tkinter.
- [ ] POST/PUT y `show ip interface brief`.
- [ ] Cuadro de confirmación DELETE y resultado.
- [ ] Ejemplo de error HTTP con barra roja.

## Pruebas

- [ ] `python3 -m unittest discover -s tests -v`.
- [ ] GUI operativa en Linux.
- [ ] Conectividad HTTPS hacia Catalyst 8000V a través de OpenConnect.
- [ ] Operaciones RESTCONF realizadas en router real.

**Rama fuente:** `feat/unidad4_act02`
