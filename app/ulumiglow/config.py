"""Configuración persistente en %APPDATA%\\UlumiGlow\\config.json."""

import json
import logging
import os

from . import DATA_DIR

PATH = os.path.join(DATA_DIR, "config.json")

DEFAULTS = {
    "enabled": True,
    "mode": "ambilight",        # ambilight | fixed | audio
    "brightness": 100,          # % aplicado antes de enviar
    "curve": "led",             # led (x^2.2) | classic (x^(1/2.2), la de v1)
    "fixed_color": "#2f7bff",
    "monitor": 1,               # índice de mss (1 = monitor principal)
    # Zona a capturar como fracción del monitor (0..1). Por defecto: 10 % superior.
    "zone": {"preset": "top", "depth": 0.10, "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.10},
    "port": "",                 # vacío = detección automática
}


def load():
    cfg = json.loads(json.dumps(DEFAULTS))  # copia profunda
    try:
        with open(PATH, encoding="utf-8") as f:
            saved = json.load(f)
        for key, value in saved.items():
            if key in cfg and isinstance(cfg[key], dict) and isinstance(value, dict):
                cfg[key].update(value)   # completa claves nuevas con valores por defecto
            elif key in cfg:
                cfg[key] = value
    except FileNotFoundError:
        pass
    except Exception as e:
        logging.warning("Config inválida, uso valores por defecto: %r", e)
    return cfg


def save(cfg):
    try:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        logging.error("No pude guardar la config: %r", e)
