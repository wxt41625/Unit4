# Validación local — Irvin Misael Mejía Hernández

Se verificó la sintaxis de los archivos Python con `python3 -m py_compile`.

Se ejecutaron **11 pruebas sin acceso al router real**, 10 pruebas de cliente HTTP simulado y una de GUI (GET, POST, PUT, DELETE) bajo un servidor gráfico virtual Xvfb:

```bash
xvfb-run -a python3 -m unittest discover -s tests -v
# Resultado: Ran 11 tests — OK
```

La prueba de GUI comprueba que el título tiene el nombre del alumno, que se muestran filas tras un GET simulado, que cambian los indicadores de estado, y que funcionan el diálogo de confirmación y el mensaje de éxito. La petición RESTCONF está simulada con `unittest.mock` y NO corresponde a una conexión real con Cisco.

Las tres imágenes `VISTA_PREVIA_*.png` son capturas reales **de la aplicación local, con interfaz sin conectar al router**. No sirven como evidencia de las operaciones RESTCONF contra IOS XE; esas capturas deben realizarse al conectarse mediante OpenConnect.
