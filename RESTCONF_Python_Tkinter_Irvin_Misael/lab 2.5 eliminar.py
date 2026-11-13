#!/usr/bin/env python3
"""Parte 2, inciso x-y: reemplazar PUT por DELETE para borrar Loopback99."""
import requests
from cli_comun import entorno_cli, informar_error
from restconf_cliente import AUTOR

requests.packages.urllib3.disable_warnings()


def main():
    host, puerto, usuario, password = entorno_cli()
    api_url = f"https://{host}:{puerto}/restconf/data/ietf-interfaces:interfaces/interface=Loopback99"
    headers = {"Accept": "application/yang-data+json", "Content-type": "application/yang-data+json"}
    basicauth = (usuario, password)
    print(f"[{AUTOR}] DELETE {api_url}")
    if input("Para borrar Loopback99 escribe ELIMINAR: ").strip() != "ELIMINAR":
        print(f"[{AUTOR}] Eliminación cancelada.")
        return 0
    try:
        # A diferencia de PUT, DELETE no envía el cuerpo JSON yangConfig.
        resp = requests.delete(api_url, auth=basicauth, headers=headers, verify=False, timeout=15)
        if 200 <= resp.status_code <= 299:
            print(f"[{AUTOR}] STATUS OK: {resp.status_code} - Loopback99 eliminada.")
            print(f"[{AUTOR}] Verifica con show ip interface brief y GET (404 después del borrado).")
            return 0
        return informar_error(resp)
    except requests.exceptions.RequestException as exc:
        print(f"[{AUTOR}] Error de red: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
