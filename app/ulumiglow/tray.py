"""Ícono en la bandeja de Windows (iconos ocultos).

Clic izquierdo: encender / apagar.  Clic derecho: menú.
"""

import threading
import time

import pystray
from PIL import Image, ImageDraw

from . import APP_NAME, resource

MODE_NAMES = {"ambilight": "Ambilight", "fixed": "Color fijo", "audio": "Audio"}


def _badge(base, on):
    """Ícono con un punto verde (encendido) o rojo (apagado)."""
    img = base.copy()
    d = ImageDraw.Draw(img)
    s = img.width
    d.ellipse((s * 0.66, s * 0.02, s * 0.98, s * 0.34),
              fill=(40, 220, 130, 255) if on else (235, 70, 70, 255),
              outline=(6, 12, 30, 255), width=max(1, s // 32))
    return img


class Tray:
    def __init__(self, app):
        self.app = app
        try:
            self.base = Image.open(resource("assets", "tray.png")).convert("RGBA").resize((64, 64))
        except Exception:
            self.base = Image.new("RGBA", (64, 64), (47, 123, 255, 255))
        self._last = None
        self.icon = pystray.Icon(APP_NAME, self._image(), APP_NAME, self._menu())

    def _image(self):
        return _badge(self.base, self.app.cfg["enabled"])

    def _menu(self):
        app, cfg = self.app, self.app.cfg

        def set_mode(name):
            return lambda: app.update({"mode": name, "enabled": True})

        def is_mode(name):
            return lambda _item: cfg["mode"] == name

        return pystray.Menu(
            pystray.MenuItem("Encendido", lambda: app.toggle(), default=True,
                             checked=lambda _i: cfg["enabled"]),
            pystray.MenuItem("Modo", pystray.Menu(*[
                pystray.MenuItem(label, set_mode(key), checked=is_mode(key), radio=True)
                for key, label in MODE_NAMES.items()
            ])),
            pystray.MenuItem("Configuración…", lambda: app.show_window()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda _i: f"ESP32: {app.device.status}", None, enabled=False),
            pystray.MenuItem("Salir", lambda: app.quit()),
        )

    def refresh(self):
        state = (self.app.cfg["enabled"], self.app.cfg["mode"])
        if state != self._last:   # el ícono solo se redibuja si cambió algo
            self._last = state
            on = "encendido" if state[0] else "apagado"
            self.icon.icon = self._image()
            self.icon.title = f"{APP_NAME} · {MODE_NAMES.get(state[1], '')} · {on}"
        self.icon.update_menu()

    def start(self):
        threading.Thread(target=self.icon.run, daemon=True, name="tray").start()
        threading.Thread(target=self._refresh_loop, daemon=True, name="tray-refresh").start()

    def _refresh_loop(self):
        while True:
            time.sleep(1.0)
            try:
                self.refresh()
            except Exception:
                pass

    def stop(self):
        try:
            self.icon.stop()
        except Exception:
            pass
