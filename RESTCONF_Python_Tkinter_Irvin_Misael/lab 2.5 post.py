#!/usr/bin/env python3
"""Complemento del nivel 2: crear Loopback99 con POST en la colección."""
import json
import requests
from cli_comun import entorno_cli, informar_error
from restconf_cliente import AUTOR, construir_yang_config

requests.packages.urllib3.disable_warnings()


def main():
    host, puerto, usuario, password = entorno_cli()
    api_url = f"https://{host}:{puerto}/restconf/data/ietf-interfaces:interfaces"
    headers = {"Accept": "application/yang-data+json", "Content-type": "application/yang-data+json"}
    basicauth = (usuario, password)
    yangConfig = construir_yang_config("Loopback99", "99.99.99.99", "255.255.255.0", f"RESTCONF - {AUTOR}")
    print(f"[{AUTOR}] POST {api_url}")
    if input("Para crear Loopback99 escribe POST: ").strip() != "POST":
        print(f"[{AUTOR}] Operación cancelada.")
        return 0
    try:
        resp = requests.post(api_url, data=json.dumps(yangConfig, ensure_ascii=False),
                             auth=basicauth, headers=headers, verify=False, timeout=15)
        if 200 <= resp.status_code <= 299:
            print(f"[{AUTOR}] STATUS OK: {resp.status_code}")
            return 0
        return informar_error(resp)
    except requests.exceptions.RequestException as exc:
        print(f"[{AUTOR}] Error de red: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
