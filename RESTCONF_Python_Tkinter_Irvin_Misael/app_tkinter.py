#!/usr/bin/env python3
"""Laboratorio RESTCONF con Python + interfaz Tkinter, Catalyst 8000V."""

from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from restconf_cliente import (
    AUTOR, ClienteRESTCONF, ErrorRESTCONF, construir_yang_config,
    interpretar_interfaces, validar_nombre,
)

BG = "#F3F6FA"
NAVY = "#12243A"
BLUE = "#1F5E91"
GREEN = "#166534"
RED = "#991B1B"


class AplicacionRESTCONF(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{AUTOR} | Cliente RESTCONF - Catalyst 8000V")
        self.geometry("1110x760")
        self.minsize(930, 650)
        self.configure(bg=BG)
        self.cola: queue.Queue = queue.Queue()
        self.ocupado = False
        self.botones: list[tk.Button] = []
        self._variables()
        self._interfaz()
        self.after(100, self._procesar_cola)

    def _variables(self):
        self.host = tk.StringVar()
        self.puerto = tk.StringVar(value="443")
        self.usuario = tk.StringVar()
        self.clave = tk.StringVar()
        self.ssl = tk.BooleanVar(value=False)
        self.nombre_consulta = tk.StringVar(value="Loopback99")
        self.nombre_config = tk.StringVar(value="Loopback99")
        self.ip_config = tk.StringVar(value="99.99.99.99")
        self.mascara_config = tk.StringVar(value="255.255.255.0")
        self.descripcion_config = tk.StringVar(value=f"RESTCONF - {AUTOR}")
        self.nombre_borrar = tk.StringVar(value="Loopback99")

    def _interfaz(self):
        estilo = ttk.Style(self)
        estilo.configure("TNotebook.Tab", padding=(17, 9), font=("DejaVu Sans", 10, "bold"))
        estilo.configure("Treeview", rowheight=27)
        estilo.configure("Treeview.Heading", font=("DejaVu Sans", 10, "bold"))

        cabecera = tk.Frame(self, bg=NAVY, padx=22, pady=15)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text="RESTCONF + PYTHON | CATALYST 8000V", bg=NAVY,
                 fg="white", font=("DejaVu Sans", 17, "bold")).pack(anchor="w")
        tk.Label(cabecera, text=f"Práctica U4ACT02  •  {AUTOR}", bg=NAVY,
                 fg="#D6E9FF", font=("DejaVu Sans", 11)).pack(anchor="w")

        # Reservar primero las franjas inferiores para que SIEMPRE se vea el estado,
        # incluso en pantallas pequeñas (Pack reserva espacio según orden de creación).
        self.estado = tk.Label(self, text=f"{AUTOR} | Listo para conectar", bg="#E2E8F0", fg=NAVY,
                               font=("DejaVu Sans", 10, "bold"), anchor="w", padx=18, pady=10)
        self.estado.pack(side="bottom", fill="x")
        pie = tk.Frame(self, bg=BG, padx=18, pady=5)
        pie.pack(side="bottom", fill="x")
        tk.Label(pie, text=f"Bitácora de {AUTOR} (no muestra contraseñas)", bg=BG,
                 fg=NAVY, font=("DejaVu Sans", 10, "bold")).pack(anchor="w")
        self.registro = ScrolledText(pie, height=3, font=("DejaVu Sans Mono", 9), wrap="word")
        self.registro.pack(fill="x", pady=(5, 5))
        self.registro.insert("end", f"[{AUTOR}] GUI iniciada. Conecta OpenConnect e introduce los datos de acceso.\n")
        self.registro.configure(state="disabled")

        conexion = ttk.LabelFrame(self, text=" Conexión RESTCONF mediante OpenConnect ", padding=14)
        conexion.pack(fill="x", padx=18, pady=(14, 8))
        for i in range(8):
            conexion.columnconfigure(i, weight=1 if i in (1, 3, 5) else 0)
        tk.Label(conexion, text="IP / hostname del router:").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=5)
        tk.Entry(conexion, textvariable=self.host, width=22).grid(row=0, column=1, sticky="ew", padx=(0, 12))
        tk.Label(conexion, text="Puerto:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        tk.Entry(conexion, textvariable=self.puerto, width=6).grid(row=0, column=3, sticky="ew", padx=(0, 12))
        tk.Label(conexion, text="Usuario:").grid(row=0, column=4, sticky="w", padx=(0, 6))
        tk.Entry(conexion, textvariable=self.usuario, width=17).grid(row=0, column=5, sticky="ew", padx=(0, 12))
        tk.Label(conexion, text="Contraseña:").grid(row=0, column=6, sticky="w", padx=(0, 6))
        tk.Entry(conexion, textvariable=self.clave, show="•", width=17).grid(row=0, column=7, sticky="ew")
        ttk.Checkbutton(conexion, text="Verificar certificado TLS (desmarcado únicamente para sandbox/laboratorio)",
                        variable=self.ssl).grid(row=1, column=0, columnspan=8, sticky="w", pady=(8, 0))

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=7)
        consulta = ttk.Frame(self.tabs, padding=15)
        config = ttk.Frame(self.tabs, padding=15)
        borrar = ttk.Frame(self.tabs, padding=15)
        self.tabs.add(consulta, text="1. Consultar (GET)")
        self.tabs.add(config, text="2. Crear / actualizar (POST / PUT)")
        self.tabs.add(borrar, text="3. Eliminar (DELETE)")
        self._tab_consulta(consulta)
        self._tab_config(config)
        self._tab_borrar(borrar)


    def _boton(self, contenedor, texto, comando, color=BLUE):
        boton = tk.Button(contenedor, text=texto, command=comando,
                          bg=color, fg="white", activebackground=NAVY, activeforeground="white",
                          font=("DejaVu Sans", 10, "bold"), padx=13, pady=7, bd=0, cursor="hand2")
        self.botones.append(boton)
        return boton

    def _tab_consulta(self, tab):
        linea = ttk.Frame(tab)
        linea.pack(fill="x", pady=(0, 12))
        tk.Label(linea, text="Nombre de interfaz:").pack(side="left", padx=(0, 8))
        tk.Entry(linea, textvariable=self.nombre_consulta, width=30).pack(side="left", padx=(0, 10), ipady=5)
        self._boton(linea, "Consultar Interfaz", self._consultar).pack(side="left", padx=(0, 8))
        self._boton(linea, "Mostrar todas", self._consultar_todas, "#475569").pack(side="left")
        tk.Label(tab, text="IP, máscara, estado administrativo y descripción (se muestran campos, no JSON sin formato)",
                 fg="#475569").pack(anchor="w", pady=(0, 8))
        tabla_frame = ttk.Frame(tab)
        tabla_frame.pack(fill="both", expand=True)
        columnas = ("nombre", "ipv4", "mascara", "estado", "descripcion")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=10)
        titulos = {"nombre": "Interfaz", "ipv4": "IPv4", "mascara": "Máscara", "estado": "Estado (admin.)", "descripcion": "Descripción"}
        anchos = {"nombre": 185, "ipv4": 140, "mascara": 140, "estado": 165, "descripcion": 330}
        for columna in columnas:
            self.tabla.heading(columna, text=titulos[columna])
            self.tabla.column(columna, width=anchos[columna], minwidth=100, stretch=(columna == "descripcion"))
        sbv = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        sbh = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sbv.set, xscrollcommand=sbh.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        sbv.grid(row=0, column=1, sticky="ns")
        sbh.grid(row=1, column=0, sticky="ew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_tabla)

    def _tab_config(self, tab):
        instrucciones = tk.Label(tab, text="Solo interfaces LoopbackN. POST crea; PUT crea o reemplaza la configuración indicada.",
                                 fg="#334155", anchor="w")
        instrucciones.pack(fill="x", pady=(0, 13))
        formulario = ttk.Frame(tab)
        formulario.pack(fill="x")
        formulario.columnconfigure(1, weight=1)
        campos = [
            ("Nombre de interfaz:", self.nombre_config),
            ("Dirección IPv4:", self.ip_config),
            ("Máscara de subred:", self.mascara_config),
            ("Descripción:", self.descripcion_config),
        ]
        for fila, (etiqueta, variable) in enumerate(campos):
            tk.Label(formulario, text=etiqueta, anchor="w").grid(row=fila, column=0, sticky="w", padx=(0, 18), pady=8)
            tk.Entry(formulario, textvariable=variable, width=55).grid(row=fila, column=1, sticky="ew", pady=8, ipady=5)
        fila_botones = ttk.Frame(tab)
        fila_botones.pack(fill="x", pady=20)
        self._boton(fila_botones, "Crear interfaz (POST)", self._crear_post).pack(side="left", padx=(0, 12))
        self._boton(fila_botones, "Crear/Actualizar Interfaz (PUT)", self._guardar_put).pack(side="left", padx=(0, 12))
        self._boton(fila_botones, "Previsualizar yangConfig", self._previsualizar, "#475569").pack(side="left")
        tk.Label(tab, text="Predeterminados del laboratorio: Loopback99, 99.99.99.99, 255.255.255.0.\n"
                 "Las operaciones POST/PUT se hacen realmente sobre el router indicado en Conexión.",
                 justify="left", fg="#64748B").pack(anchor="w", pady=(0, 5))

    def _tab_borrar(self, tab):
        tk.Label(tab, text="La eliminación es permanente en la configuración activa del dispositivo.\n"
                 "Para evitar perder acceso a la VPN, el programa no permite borrar interfaces físicas.",
                 fg=RED, justify="left").pack(anchor="w", pady=(0, 22))
        linea = ttk.Frame(tab)
        linea.pack(anchor="w", fill="x")
        tk.Label(linea, text="Interfaz a eliminar:").pack(side="left", padx=(0, 12))
        tk.Entry(linea, textvariable=self.nombre_borrar, width=30).pack(side="left", ipady=5, padx=(0, 15))
        self._boton(linea, "Eliminar Interfaz", self._eliminar, "#B91C1C").pack(side="left")
        tk.Label(tab, text="Antes de DELETE se abrirá messagebox.askyesno() para confirmar o cancelar.",
                 fg="#475569").pack(anchor="w", pady=20)

    def _seleccionar_tabla(self, _evento):
        seleccion = self.tabla.selection()
        if seleccion:
            nombre = self.tabla.item(seleccion[0], "values")[0]
            self.nombre_consulta.set(nombre)
            if nombre.lower().startswith("loopback"):
                self.nombre_borrar.set(nombre)
                self.nombre_config.set(nombre)

    def _construir_cliente(self) -> ClienteRESTCONF:
        try:
            puerto = int(self.puerto.get())
        except ValueError as exc:
            raise ValueError("El puerto HTTPS debe ser un número entero.") from exc
        return ClienteRESTCONF(self.host.get(), self.usuario.get(), self.clave.get(), puerto, self.ssl.get())

    def _cambiar_estado(self, mensaje, color):
        fondos = {"verde": ("#DCFCE7", GREEN), "rojo": ("#FEE2E2", RED), "espera": ("#DBEAFE", BLUE)}
        bg, fg = fondos.get(color, ("#E2E8F0", NAVY))
        self.estado.config(text=f"{AUTOR} | {mensaje}", bg=bg, fg=fg)

    def _log(self, mensaje):
        self.registro.configure(state="normal")
        self.registro.insert("end", f"[{AUTOR}] {mensaje}\n")
        self.registro.see("end")
        self.registro.configure(state="disabled")

    def _error_validacion(self, exc):
        self._cambiar_estado(str(exc), "rojo")
        self._log(f"ERROR local: {exc}")
        messagebox.showerror(f"{AUTOR} - Validación", str(exc), parent=self)

    def _ejecutar(self, etiqueta, accion, al_terminar):
        if self.ocupado:
            return
        try:
            cliente = self._construir_cliente()
        except ValueError as exc:
            self._error_validacion(exc)
            return
        self.ocupado = True
        for boton in self.botones:
            boton.configure(state="disabled")
        self._cambiar_estado(f"Consultando router... {etiqueta}", "espera")
        self._log(f"Enviando {etiqueta} a {cliente.base_url} (sin mostrar credenciales)")

        def trabajo():
            try:
                resultado = accion(cliente)
                self.cola.put((True, resultado, al_terminar, etiqueta))
            except (ErrorRESTCONF, ValueError, KeyError) as exc:
                self.cola.put((False, exc, None, etiqueta))
            except Exception as exc:
                self.cola.put((False, ErrorRESTCONF(f"Error inesperado: {type(exc).__name__}: {exc}"), None, etiqueta))

        threading.Thread(target=trabajo, daemon=True).start()

    def _procesar_cola(self):
        try:
            while True:
                correcto, valor, callback, etiqueta = self.cola.get_nowait()
                self.ocupado = False
                for boton in self.botones:
                    boton.configure(state="normal")
                if correcto:
                    self._cambiar_estado(f"Operación exitosa | HTTP {valor.codigo} | {etiqueta}", "verde")
                    self._log(f"{etiqueta}: HTTP {valor.codigo} (operación exitosa)")
                    try:
                        callback(valor)
                    except (ErrorRESTCONF, ValueError) as exc:
                        self._error_validacion(exc)
                else:
                    self._cambiar_estado(f"Error: {valor}", "rojo")
                    self._log(f"{etiqueta}: {valor}")
                    if etiqueta.startswith("GET"):
                        self.tabla.delete(*self.tabla.get_children())
                    messagebox.showerror(f"{AUTOR} - Error RESTCONF", str(valor), parent=self)
        except queue.Empty:
            pass
        self.after(100, self._procesar_cola)

    def _mostrar_filas(self, resultado):
        filas = interpretar_interfaces(resultado.datos)
        self.tabla.delete(*self.tabla.get_children())
        for fila in filas:
            self.tabla.insert("", "end", values=(fila["nombre"], fila["ipv4"], fila["mascara"],
                                                   fila["estado"], fila["descripcion"]))
        self._log(f"GET mostró {len(filas)} fila(s) en la tabla de interfaces")

    def _consultar(self):
        try:
            nombre = validar_nombre(self.nombre_consulta.get())
        except ValueError as exc:
            self._error_validacion(exc)
            return
        self._ejecutar(f"GET {nombre}", lambda cliente: cliente.consultar_interfaz(nombre), self._mostrar_filas)

    def _consultar_todas(self):
        self._ejecutar("GET todas las interfaces", lambda cliente: cliente.consultar_todas(), self._mostrar_filas)

    def _config(self):
        return construir_yang_config(self.nombre_config.get(), self.ip_config.get(),
                                     self.mascara_config.get(), self.descripcion_config.get())

    def _previsualizar(self):
        try:
            yangConfig = self._config()
        except ValueError as exc:
            self._error_validacion(exc)
            return
        ventana = tk.Toplevel(self)
        ventana.title(f"{AUTOR} | Previsualización del JSON yangConfig")
        ventana.geometry("650x480")
        panel = ScrolledText(ventana, font=("DejaVu Sans Mono", 10), wrap="none", padx=13, pady=13)
        panel.pack(fill="both", expand=True)
        panel.insert("1.0", json.dumps(yangConfig, indent=4, ensure_ascii=False))
        panel.configure(state="disabled")

    def _aviso_exito(self, respuesta):
        messagebox.showinfo(f"{AUTOR} - Operación exitosa",
                            f"RESTCONF respondió HTTP {respuesta.codigo}.\n"
                            "Verifica la interfaz con un GET y con 'show ip interface brief' en el Catalyst.",
                            parent=self)

    def _crear_post(self):
        try:
            datos = self._config()
        except ValueError as exc:
            self._error_validacion(exc)
            return
        self._ejecutar("POST interfaz", lambda cliente: cliente.crear_post(datos), self._aviso_exito)

    def _guardar_put(self):
        try:
            datos = self._config()
        except ValueError as exc:
            self._error_validacion(exc)
            return
        nombre = datos["ietf-interfaces:interface"]["name"]
        if not messagebox.askyesno(f"{AUTOR} - Confirmar PUT",
                                   f"PUT puede reemplazar la configuración existente de {nombre}.\n"
                                   "¿Deseas crear o actualizar esta Loopback?", parent=self):
            self._log(f"PUT {nombre} cancelado por el usuario")
            return
        self._ejecutar(f"PUT {nombre}", lambda cliente: cliente.guardar_put(datos), self._aviso_exito)

    def _eliminar(self):
        try:
            nombre = validar_nombre(self.nombre_borrar.get(), solo_loopback=True)
        except ValueError as exc:
            self._error_validacion(exc)
            return
        if not messagebox.askyesno(f"{AUTOR} - Confirmar eliminación",
                                   f"¿Seguro que quieres ELIMINAR {nombre} del Catalyst 8000V?\n"
                                   "Esta acción enviará una petición RESTCONF DELETE.",
                                   icon="warning", parent=self):
            self._log(f"DELETE {nombre} cancelado por el usuario")
            return
        self._ejecutar(f"DELETE {nombre}", lambda cliente: cliente.borrar(nombre), self._aviso_exito)


def main():
    print(f"[{AUTOR}] Iniciando aplicación RESTCONF con Tkinter para Catalyst 8000V.")
    print(f"[{AUTOR}] No se guardan credenciales; primero conecta la VPN con OpenConnect.")
    AplicacionRESTCONF().mainloop()


if __name__ == "__main__":
    main()
