"""Ventana de configuración (pywebview + HTML/CSS en ui/web).

La parte visual vive en ui/web. Este archivo solo expone al JavaScript
las funciones del programa (clase Api) y crea la ventana.
"""

import base64
import io

import webview
from PIL import Image

from .. import APP_NAME, VERSION, resource
from ..device import list_ports


class Api:
    """Todo lo que la interfaz puede pedirle al programa (window.pywebview.api)."""

    def __init__(self, app):
        self._app = app  # con "_" para que pywebview no lo exponga

    def get_state(self):
        app = self._app
        intro, app.show_intro = app.show_intro, False   # la intro sale una sola vez
        return {
            "config": app.cfg,
            "monitors": self.get_monitors(),
            "ports": list_ports(),
            "intro": intro,
            "version": VERSION,
        }

    def get_status(self):
        app = self._app
        return {
            "rgb": list(app.engine.last_rgb),
            "connected": app.device.connected,
            "status": app.device.status,
            "enabled": app.cfg["enabled"],
            "mode": app.cfg["mode"],
        }

    def set_config(self, patch):
        self._app.update(patch)
        return self._app.cfg

    def get_ports(self):
        return list_ports()

    def get_monitors(self):
        import mss
        with mss.mss() as sct:
            return [{"index": i, "width": m["width"], "height": m["height"]}
                    for i, m in enumerate(sct.monitors) if i > 0]

    def get_screenshot(self, monitor):
        """Captura reducida del monitor para el mapa de zonas (data URL JPEG)."""
        import mss
        with mss.mss() as sct:
            mons = sct.monitors
            shot = sct.grab(mons[monitor if 1 <= monitor < len(mons) else 1])
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        img.thumbnail((720, 720))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=80)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    def hide(self):
        self._app.hide_window()

    def minimize(self):
        self._app.window.minimize()

    def quit(self):
        self._app.quit()


def create_window(app, hidden):
    return webview.create_window(
        APP_NAME,
        url=resource("ulumiglow", "ui", "web", "index.html"),
        js_api=Api(app),
        width=1040, height=680, min_size=(920, 620),
        frameless=True, easy_drag=False,
        background_color="#050a1c",
        hidden=hidden,
    )


def run():
    webview.start(debug=False)
