"""Pruebas totalmente locales: NO contactan al Catalyst 8000V."""
import json
import unittest
from unittest.mock import patch

import requests

from restconf_cliente import (
    ClienteRESTCONF, ErrorRESTCONF, construir_yang_config, interpretar_interfaces,
    validar_nombre,
)


class RespuestaFalsa:
    def __init__(self, codigo=200, contenido=None, texto=""):
        self.status_code = codigo
        self._contenido = contenido
        self.text = texto
        self.content = json.dumps(contenido).encode() if contenido is not None else b""

    def json(self):
        if self._contenido is None:
            raise ValueError("No JSON")
        return self._contenido


class PruebasRESTCONF(unittest.TestCase):
    def setUp(self):
        self.cliente = ClienteRESTCONF("192.0.2.10", "usuario_prueba", "clave_prueba")
        self.config = construir_yang_config("Loopback99", "99.99.99.99", "255.255.255.0", "IRVIN")

    def test_estructura_yang_config(self):
        interfaz = self.config["ietf-interfaces:interface"]
        self.assertEqual(interfaz["name"], "Loopback99")
        self.assertEqual(interfaz["type"], "iana-if-type:softwareLoopback")
        self.assertEqual(interfaz["ietf-ip:ipv4"]["address"][0]["netmask"], "255.255.255.0")
        self.assertIs(interfaz["enabled"], True)
        self.assertEqual(interfaz["description"], "IRVIN")

    def test_validacion_ip_mascara_y_tipo(self):
        for ip, mascara in [("999.1.1.1", "255.255.255.0"), ("99.99.99.99", "255.0.255.0")]:
            with self.assertRaises(ValueError):
                construir_yang_config("Loopback99", ip, mascara, "prueba")
        with self.assertRaises(ValueError):
            construir_yang_config("GigabitEthernet1", "99.99.99.99", "255.255.255.0", "prueba")
        self.assertEqual(validar_nombre("GigabitEthernet1"), "GigabitEthernet1")

    @patch("restconf_cliente.requests.get")
    def test_get_por_interfaz(self, funcion):
        contenido = {"ietf-interfaces:interface": {
            "name": "Loopback99", "enabled": True,
            "ietf-ip:ipv4": {"address": [{"ip": "99.99.99.99", "netmask": "255.255.255.0"}]}}}
        funcion.return_value = RespuestaFalsa(200, contenido)
        resultado = self.cliente.consultar_interfaz("Loopback99")
        self.assertEqual(resultado.codigo, 200)
        self.assertEqual(interpretar_interfaces(resultado.datos)[0]["ipv4"], "99.99.99.99")
        url = funcion.call_args.args[0]
        self.assertTrue(url.endswith("/interface=Loopback99"))
        self.assertEqual(funcion.call_args.kwargs["headers"]["Accept"], "application/yang-data+json")
        self.assertEqual(funcion.call_args.kwargs["auth"], ("usuario_prueba", "clave_prueba"))

    @patch("restconf_cliente.requests.get")
    def test_get_todas_interfaz_con_mascara_prefijo(self, funcion):
        contenido = {"ietf-interfaces:interfaces": {"interface": [
            {"name": "GigabitEthernet1", "enabled": False,
             "ietf-ip:ipv4": {"address": [{"ip": "10.0.0.1", "prefix-length": 24}]}},
            {"name": "Loopback99", "enabled": True, "ietf-ip:ipv4": {}},
        ]}}
        funcion.return_value = RespuestaFalsa(200, contenido)
        filas = interpretar_interfaces(self.cliente.consultar_todas().datos)
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[0]["mascara"], "255.255.255.0")
        self.assertEqual(filas[0]["estado"], "Deshabilitada")
        self.assertEqual(filas[1]["ipv4"], "-")

    @patch("restconf_cliente.requests.post")
    def test_post_201_created(self, funcion):
        funcion.return_value = RespuestaFalsa(201)
        resultado = self.cliente.crear_post(self.config)
        self.assertEqual(resultado.codigo, 201)
        self.assertTrue(funcion.call_args.args[0].endswith("/ietf-interfaces:interfaces"))
        self.assertEqual(json.loads(funcion.call_args.kwargs["data"]), self.config)

    @patch("restconf_cliente.requests.put")
    def test_put_200(self, funcion):
        funcion.return_value = RespuestaFalsa(200)
        resultado = self.cliente.guardar_put(self.config)
        self.assertEqual(resultado.codigo, 200)
        self.assertTrue(funcion.call_args.args[0].endswith("interface=Loopback99"))

    @patch("restconf_cliente.requests.delete")
    def test_delete_204(self, funcion):
        funcion.return_value = RespuestaFalsa(204)
        self.assertEqual(self.cliente.borrar("Loopback99").codigo, 204)
        funcion.assert_called_once()
        with self.assertRaises(ValueError):
            self.cliente.borrar("GigabitEthernet1")

    @patch("restconf_cliente.requests.get")
    def test_http_401_404_500(self, funcion):
        for codigo in [401, 404, 500]:
            funcion.return_value = RespuestaFalsa(codigo, {"errors": {"error": [{"error-message": "prueba"}]}})
            with self.assertRaises(ErrorRESTCONF) as contexto:
                self.cliente.consultar_interfaz("Loopback99")
            self.assertEqual(contexto.exception.codigo, codigo)

    @patch("restconf_cliente.requests.get")
    def test_red_timeout(self, funcion):
        funcion.side_effect = requests.exceptions.Timeout("timeout de prueba")
        with self.assertRaises(ErrorRESTCONF) as contexto:
            self.cliente.consultar_todas()
        self.assertIn("VPN", str(contexto.exception))

    def test_impide_host_con_url_o_puerto_incrustado(self):
        for host in ["https://192.0.2.10", "192.0.2.10:443", "192.0.2.10/restconf"]:
            with self.assertRaises(ValueError):
                ClienteRESTCONF(host, "u", "p")


if __name__ == "__main__":
    unittest.main()
