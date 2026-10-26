"""Une todas las piezas: config, ESP32, motor, bandeja y ventana."""

import logging
import threading

from . import config
from .device import Device
from .engine import Engine
from .tray import Tray
from .ui import window as ui


class App:
    def __init__(self, show_intro):
        self.cfg = config.load()
        self.device = Device(self.cfg["port"])
        self.engine = Engine(self.cfg, self.device)
        self.show_intro = show_intro
        self.window = None
        self.tray = None
        self._quitting = False

    # ---- acciones (las usan la bandeja y la interfaz) ----
    def update(self, patch):
        for key, value in patch.items():
            if key in self.cfg:
                self.cfg[key] = value
        if "port" in patch:
            self.device.set_port(self.cfg["port"])
        config.save(self.cfg)
        self.engine.poke()
        if self.tray:
            self.tray.refresh()

    def toggle(self):
        self.update({"enabled": not self.cfg["enabled"]})

    def show_window(self):
        if self.window:
            self.window.show()
            self.window.restore()

    def hide_window(self):
        if self.window:
            self.window.hide()

    def quit(self):
        logging.info("Salir")
        self._quitting = True
        self.engine.stop()
        if self.tray:
            self.tray.stop()
        if self.window:
            self.window.destroy()

    def _on_closing(self):
        # Cerrar la ventana (Alt+F4) la manda a la bandeja; "Salir" cierra de verdad.
        # hide() se llama en otro hilo: dentro de este evento cuelga pywebview.
        if not self._quitting:
            threading.Thread(target=self.hide_window, daemon=True).start()
            return False
        return True

    # ---- arranque ----
    def run(self, start_hidden):
        self.engine.start()
        self.tray = Tray(self)
        self.tray.start()
        self.window = ui.create_window(self, hidden=start_hidden)
        self.window.events.closing += self._on_closing
        ui.run()   # bloquea hasta que se destruye la ventana
