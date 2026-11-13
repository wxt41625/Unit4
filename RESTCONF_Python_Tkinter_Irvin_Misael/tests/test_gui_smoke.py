"""Smoke test GUI bajo Xvfb: solicitudes SIMULADAS, no router real."""
import os
import time
import unittest
from unittest.mock import patch

from restconf_cliente import ErrorRESTCONF, Respuesta


@unittest.skipUnless(os.environ.get("DISPLAY"), "GUI requiere DISPLAY o xvfb-run")
class PruebaGUI(unittest.TestCase):
    def test_get_put_post_delete_y_estado(self):
        from app_tkinter import AplicacionRESTCONF

        payload = {"ietf-interfaces:interface": {
            "name": "Loopback99", "description": "RESTCONF - Irvin Misael Mejía Hernández",
            "enabled": True, "ietf-ip:ipv4": {"address": [{
                "ip": "99.99.99.99", "netmask": "255.255.255.0"
            }]}
        }}

        class RouterSimulado:
            eliminada = False
            base_url = "https://192.0.2.1:443"
            def consultar_interfaz(self, nombre):
                if self.eliminada:
                    raise ErrorRESTCONF("HTTP 404: Interfaz no encontrada", 404)
                return Respuesta(200, payload, "", "GET", f"{self.base_url}/{nombre}")
            def consultar_todas(self):
                return Respuesta(200, {"ietf-interfaces:interfaces": {
                    "interface": [payload["ietf-interfaces:interface"]]
                }}, "", "GET", self.base_url)
            def crear_post(self, config):
                return Respuesta(201, None, "", "POST", self.base_url)
            def guardar_put(self, config):
                return Respuesta(200, None, "", "PUT", self.base_url)
            def borrar(self, nombre):
                self.eliminada = True
                return Respuesta(204, None, "", "DELETE", self.base_url)

        def hasta_terminar(app):
            for _ in range(200):
                app.update()
                if not app.ocupado and app.cola.empty():
                    app.update()
                    return
                time.sleep(0.01)
            self.fail("La GUI no terminó la operación RESTCONF simulada")

        with patch("app_tkinter.ClienteRESTCONF", return_value=RouterSimulado()), \
             patch("app_tkinter.messagebox.showinfo") as exito, \
             patch("app_tkinter.messagebox.showerror") as error, \
             patch("app_tkinter.messagebox.askyesno", return_value=True) as confirmacion:
            app = AplicacionRESTCONF()
            try:
                app.withdraw()
                self.assertIn("Irvin Misael Mejía Hernández", app.title())
                app._consultar()
                hasta_terminar(app)
                self.assertEqual(len(app.tabla.get_children()), 1)
                self.assertIn("Operación exitosa", app.estado.cget("text"))
                app._consultar_todas()
                hasta_terminar(app)
                self.assertEqual(len(app.tabla.get_children()), 1)
                app._crear_post()
                hasta_terminar(app)
                app._guardar_put()
                hasta_terminar(app)
                app._eliminar()
                hasta_terminar(app)
                self.assertEqual(exito.call_count, 3)
                self.assertEqual(error.call_count, 0)
                self.assertEqual(confirmacion.call_count, 2)
                self.assertIn("HTTP 204", app.estado.cget("text"))
                app._consultar()
                hasta_terminar(app)
                self.assertEqual(error.call_count, 1)
                self.assertIn("404", app.estado.cget("text"))
                self.assertEqual(app.estado.cget("bg"), "#FEE2E2")
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
