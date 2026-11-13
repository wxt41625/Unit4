"""Cliente RESTCONF básico para IOS XE (Catalyst 8000V).

Autor académico: Irvin Misael Mejía Hernández
Solo se permite escribir / borrar LoopbackN para proteger la red de gestión.
"""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import json
import re
from typing import Any
from urllib.parse import quote

import requests
from requests.exceptions import RequestException

AUTOR = "Irvin Misael Mejía Hernández"
TIPO_JSON = "application/yang-data+json"
BASE_DATOS = "/restconf/data/ietf-interfaces:interfaces"
PATRON_NOMBRE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:/-]{0,79}$")
PATRON_LOOPBACK = re.compile(r"^Loopback\d{1,6}$", re.IGNORECASE)


class ErrorRESTCONF(Exception):
    """Error legible para la GUI o la terminal."""

    def __init__(self, mensaje: str, codigo: int | None = None):
        super().__init__(mensaje)
        self.codigo = codigo


@dataclass
class Respuesta:
    codigo: int
    datos: Any
    texto: str
    metodo: str
    url: str


def validar_nombre(nombre: str, solo_loopback: bool = False) -> str:
    nombre = nombre.strip()
    if not PATRON_NOMBRE.fullmatch(nombre):
        raise ValueError("Escribe un nombre de interfaz válido, por ejemplo Loopback99 o GigabitEthernet1.")
    if solo_loopback and not PATRON_LOOPBACK.fullmatch(nombre):
        raise ValueError("Por seguridad solo se permite crear, actualizar o borrar interfaces LoopbackN.")
    return nombre


def construir_yang_config(nombre: str, ip: str, mascara: str, descripcion: str) -> dict:
    """Convierte los valores de las entradas GUI a un diccionario yangConfig."""
    nombre = validar_nombre(nombre, solo_loopback=True)
    try:
        ip = str(ipaddress.IPv4Address(ip.strip()))
    except ipaddress.AddressValueError as exc:
        raise ValueError("La dirección IPv4 no es válida.") from exc
    mascara = mascara.strip()
    try:
        # El constructor comprueba que la máscara sea contigua y válida.
        red = ipaddress.IPv4Network(f"0.0.0.0/{mascara}")
        mascara = str(red.netmask)
    except (ValueError, ipaddress.NetmaskValueError) as exc:
        raise ValueError("La máscara no es válida. Ejemplo: 255.255.255.0.") from exc
    descripcion = descripcion.strip()
    if not descripcion:
        raise ValueError("Escribe una descripción para identificar tu interfaz.")
    if len(descripcion) > 180:
        raise ValueError("Usa una descripción de máximo 180 caracteres.")

    yangConfig = {
        "ietf-interfaces:interface": {
            "name": nombre,
            "description": descripcion,
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {"address": [{"ip": ip, "netmask": mascara}]},
            "ietf-ip:ipv6": {},
        }
    }
    return yangConfig


def interpretar_interfaces(datos: Any) -> list[dict]:
    """Interpreta la respuesta GET de todas las interfaces o una interfaz específica."""
    if not isinstance(datos, dict):
        raise ErrorRESTCONF("La respuesta no es un objeto JSON YANG válido.")
    lista = None
    for clave in ("ietf-interfaces:interfaces", "interfaces"):
        contenedor = datos.get(clave)
        if isinstance(contenedor, dict):
            lista = contenedor.get("interface", contenedor.get("ietf-interfaces:interface"))
            break
    if lista is None:
        lista = datos.get("ietf-interfaces:interface", datos.get("interface"))
    if lista is None:
        raise ErrorRESTCONF("El JSON no contiene la estructura ietf-interfaces esperada.")
    if isinstance(lista, dict):
        lista = [lista]
    if not isinstance(lista, list):
        raise ErrorRESTCONF("El recurso interface recibido tiene un formato no compatible.")
    filas: list[dict] = []
    for interfaz in lista:
        if not isinstance(interfaz, dict):
            continue
        nombre = str(interfaz.get("name", "Desconocida"))
        habilitado = interfaz.get("enabled")
        estado = "Habilitada" if habilitado is True else "Deshabilitada" if habilitado is False else "Sin dato"
        ipv4 = interfaz.get("ietf-ip:ipv4", interfaz.get("ipv4", {}))
        direcciones = ipv4.get("address", []) if isinstance(ipv4, dict) else []
        if not isinstance(direcciones, list) or not direcciones:
            direcciones = [{}]
        for direccion in direcciones:
            if not isinstance(direccion, dict):
                direccion = {}
            prefijo = direccion.get("prefix-length")
            mascara = direccion.get("netmask", "-")
            if mascara == "-" and isinstance(prefijo, int):
                try:
                    mascara = str(ipaddress.IPv4Network(f"0.0.0.0/{prefijo}").netmask)
                except ValueError:
                    pass
            filas.append({
                "nombre": nombre,
                "ipv4": str(direccion.get("ip", "-")),
                "mascara": str(mascara),
                "estado": estado,
                "descripcion": str(interfaz.get("description", "-")),
            })
    return filas


class ClienteRESTCONF:
    def __init__(self, host: str, usuario: str, password: str, puerto: int = 443,
                 verificar_ssl: bool = False, timeout: int = 15):
        host = host.strip()
        if not host or any(c in host for c in ("/", "\\", "@", "?", "#", " ")) or ":" in host:
            raise ValueError("Ingresa únicamente la IP o hostname del router, sin https://, ruta ni puerto.")
        if not usuario.strip() or not password:
            raise ValueError("Es necesario indicar usuario y contraseña del Catalyst 8000V.")
        if not isinstance(puerto, int) or not 1 <= puerto <= 65535:
            raise ValueError("El puerto HTTPS debe estar entre 1 y 65535.")
        self.base_url = f"https://{host}:{puerto}"
        self.headers = {"Accept": TIPO_JSON, "Content-type": TIPO_JSON}
        self.basicauth = (usuario.strip(), password)
        self.verificar_ssl = verificar_ssl
        self.timeout = timeout
        if not verificar_ssl:
            # Se reproduce el procedimiento del PDF, solo adecuado para laboratorio.
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
            )

    def _enviar(self, metodo: str, ruta: str, datos: dict | None = None) -> Respuesta:
        url = self.base_url + ruta
        argumentos = {
            "auth": self.basicauth,
            "headers": self.headers,
            "verify": self.verificar_ssl,
            "timeout": self.timeout,
        }
        if datos is not None:
            argumentos["data"] = json.dumps(datos, ensure_ascii=False)
        try:
            # GET/POST/PUT/DELETE explícitos, equivalentes a requests.get(), etc.
            llamada = {
                "GET": requests.get,
                "POST": requests.post,
                "PUT": requests.put,
                "DELETE": requests.delete,
            }[metodo]
            respuesta = llamada(url, **argumentos)
        except RequestException as exc:
            raise ErrorRESTCONF(f"Fallo de red, VPN o TLS: {exc.__class__.__name__}: {exc}") from exc
        try:
            contenido = respuesta.json() if respuesta.content else None
        except ValueError:
            contenido = None
        if not 200 <= respuesta.status_code <= 299:
            codigos = {
                400: "Solicitud inválida o JSON YANG no aceptado",
                401: "No autorizado: verifica usuario y contraseña",
                403: "Acceso denegado: revisa permisos del usuario",
                404: "Interfaz o recurso RESTCONF no encontrado",
                405: "El método HTTP no está permitido",
                409: "Conflicto: la interfaz ya existe o tiene dependencias",
                415: "El formato application/yang-data+json no fue aceptado",
                500: "Error interno de IOS XE o del servicio RESTCONF",
            }
            explicacion = codigos.get(respuesta.status_code, "El router rechazó la petición")
            if isinstance(contenido, dict):
                detalle = json.dumps(contenido, ensure_ascii=False)[:400]
            else:
                detalle = (respuesta.text or "(sin detalle)")[:400]
            raise ErrorRESTCONF(f"HTTP {respuesta.status_code}: {explicacion}. Respuesta: {detalle}", respuesta.status_code)
        return Respuesta(respuesta.status_code, contenido, respuesta.text or "", metodo, url)

    def consultar_todas(self) -> Respuesta:
        return self._enviar("GET", BASE_DATOS)

    def consultar_interfaz(self, nombre: str) -> Respuesta:
        nombre = validar_nombre(nombre)
        return self._enviar("GET", f"{BASE_DATOS}/interface={quote(nombre, safe='')}")

    def crear_post(self, config: dict) -> Respuesta:
        validar_nombre(config["ietf-interfaces:interface"]["name"], solo_loopback=True)
        return self._enviar("POST", BASE_DATOS, config)

    def guardar_put(self, config: dict) -> Respuesta:
        nombre = validar_nombre(config["ietf-interfaces:interface"]["name"], solo_loopback=True)
        return self._enviar("PUT", f"{BASE_DATOS}/interface={quote(nombre, safe='')}", config)

    def borrar(self, nombre: str) -> Respuesta:
        nombre = validar_nombre(nombre, solo_loopback=True)
        return self._enviar("DELETE", f"{BASE_DATOS}/interface={quote(nombre, safe='')}")
