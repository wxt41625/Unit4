#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! python3 -c 'import tkinter' 2>/dev/null; then
  printf 'Falta Tkinter. En Debian/antiX: sudo apt install python3-tk python3-venv\n'
  exit 1
fi
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app_tkinter.py
