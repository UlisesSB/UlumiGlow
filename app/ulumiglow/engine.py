"""Motor: hilo que calcula el color del modo activo y lo envía al ESP32."""

import logging
import threading

from . import color
from .modes import MODES

BLACK = (0, 0, 0)


class Engine(threading.Thread):
    def __init__(self, cfg, device):
        super().__init__(daemon=True, name="engine")
        self.cfg = cfg
        self.device = device
        self.modes = {name: cls(cfg) for name, cls in MODES.items()}
        self.last_rgb = BLACK
        self._active = None
        self._quit = threading.Event()
        self._wake = threading.Event()

    def poke(self):
        """Avisa que cambió la config para reaccionar sin esperar."""
        self._wake.set()

    def run(self):
        while not self._quit.is_set():
            try:
                interval = self._step()
            except Exception:
                logging.exception("Error en el motor")
                interval = 1.0
            self._wake.wait(interval)
            self._wake.clear()

    def _step(self):
        if not self.device.ensure():
            return 0.5

        if not self.cfg["enabled"]:
            self._switch(None)
            self.device.send(BLACK, hold=True)   # pausa = apagado fijo
            self.last_rgb = BLACK
            return 1.0

        mode = self.modes.get(self.cfg["mode"], self.modes["ambilight"])
        self._switch(mode)
        rgb = color.output(mode.color(), self.cfg["curve"], self.cfg["brightness"])
        self.device.send(rgb, hold=mode.hold)
        self.last_rgb = rgb
        return mode.interval

    def _switch(self, mode):
        """Libera los recursos del modo anterior (p. ej. la captura de audio)."""
        if mode is not self._active and self._active is not None:
            self._active.close()
        self._active = mode

    def stop(self):
        self._quit.set()
        self._wake.set()
        self.join(timeout=3)
        # Al salir, el color fijo queda puesto; Ambilight y Audio se apagan.
        if not (self.cfg["enabled"] and self.cfg["mode"] == "fixed"):
            self.device.send(BLACK, hold=True)
        self.device.close()
        for mode in self.modes.values():
            mode.close()
