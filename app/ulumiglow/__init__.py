"""UlumiGlow - Sistema Ambilight para PC con ESP32-C3.

Copyright (c) 2025-2026 Ulises Agustin Rodriguez - Licencia MIT
"""

import os
import sys

APP_NAME = "UlumiGlow"
VERSION = "2.0.0"

# Carpeta de datos del usuario (config + log): %APPDATA%\UlumiGlow
DATA_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~/.config"), APP_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

# Carpeta de recursos (assets y web). Con PyInstaller viven en sys._MEIPASS.
RES_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resource(*parts):
    return os.path.join(RES_DIR, *parts)
