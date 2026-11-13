#!/usr/bin/env python3
"""Parte 1, pasos 1-4: RESTCONF GET y salida JSON formateada."""
import json
import requests
from cli_comun import entorno_cli, informar_error
from restconf_cliente import AUTOR

requests.packages.urllib3.disable_warnings()


def main():
    host, puerto, usuario, password = entorno_cli()
    api_url = f"https://{host}:{puerto}/restconf/data/ietf-interfaces:interfaces"
    headers = {"Accept": "application/yang-data+json", "Content-type": "application/yang-data+json"}
    basicauth = (usuario, password)

    print(f"[{AUTOR}] GET {api_url}")
    try:
        resp = requests.get(api_url, auth=basicauth, headers=headers, verify=False, timeout=15)
        if not 200 <= resp.status_code <= 299:
            return informar_error(resp)
        response_json = resp.json()
        print(f"[{AUTOR}] STATUS OK: {resp.status_code}")
        print(json.dumps(response_json, indent=4, ensure_ascii=False))
        return 0
    except (requests.exceptions.RequestException, ValueError) as exc:
        print(f"[{AUTOR}] Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
