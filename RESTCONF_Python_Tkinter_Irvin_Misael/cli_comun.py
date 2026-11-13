"""Lectura segura de credenciales desde terminal para los scripts de NetAcad."""
import getpass
import os
import sys

from restconf_cliente import AUTOR


def entorno_cli():
    print(f"\n[{AUTOR}] LAB U4ACT02 - RESTCONF con Python - Catalyst 8000V")
    print(f"[{AUTOR}] Asegúrate de que OpenConnect ya está conectado.")
    host = os.getenv("RESTCONF_HOST") or input("IP/hostname del Catalyst 8000V: ").strip()
    usuario = os.getenv("RESTCONF_USER") or input("Usuario RESTCONF: ").strip()
    password = os.getenv("RESTCONF_PASSWORD") or getpass.getpass("Contraseña RESTCONF (oculta): ")
    puerto = int(os.getenv("RESTCONF_PORT", "443"))
    if not host or any(c in host for c in ("/", "\\", "@", "?", "#", " ", ":")):
        raise ValueError("El host debe ser solo una IPv4/hostname, sin https:// ni puerto.")
    if not usuario or not password:
        raise ValueError("Usuario y contraseña son obligatorios.")
    return host, puerto, usuario, password


def informar_error(respuesta):
    try:
        detalle = respuesta.json()
    except ValueError:
        detalle = respuesta.text
    print(f"[{AUTOR}] HTTP {respuesta.status_code}: {str(detalle)[:800]}", file=sys.stderr)
    return 1
