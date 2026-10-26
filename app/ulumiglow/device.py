"""Conexión USB con el ESP32: detección, reconexión y envío de colores.

Protocolo (ver firmware/src/main.cpp):
    0xAA R G B  color en vivo; el ESP32 apaga la tira si deja de recibirlos.
    0xAB R G B  color fijo; queda puesto aunque la PC deje de enviar.
"""

import logging
import re
import time

import serial
import serial.tools.list_ports

BAUD = 115200
RETRY_SEC = 2.0
HDR_STREAM = 0xAA
HDR_HOLD = 0xAB

ESPRESSIF_VIDS = {"303A"}
KEYWORDS = ["usb serial/jtag", "esp32", "cp210", "ch340", "silicon labs", "wch"]


def list_ports():
    return [p.device for p in serial.tools.list_ports.comports()]


def autodetect():
    """Devuelve el COM del ESP32 o None. Prioriza el VID de Espressif."""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        m = re.search(r"VID:PID=([0-9A-F]{4}):", (p.hwid or "").upper())
        if m and m.group(1) in ESPRESSIF_VIDS:
            return p.device
    for p in ports:
        text = f"{p.description or ''} {p.hwid or ''}".lower()
        if any(k in text for k in KEYWORDS):
            return p.device
    return None


class Device:
    def __init__(self, port_setting=""):
        self.port_setting = port_setting  # "" = automático
        self.ser = None
        self.port = None
        self.status = "Buscando ESP32…"
        self._next_try = 0.0

    @property
    def connected(self):
        return self.ser is not None

    def ensure(self):
        """Intenta conectar si no hay conexión (como mucho cada RETRY_SEC)."""
        if self.ser:
            return True
        if time.monotonic() < self._next_try:
            return False
        self._next_try = time.monotonic() + RETRY_SEC

        port = self.port_setting or autodetect()
        if not port:
            self.status = "ESP32 no detectado"
            return False
        try:
            self.ser = serial.Serial(port, BAUD, timeout=0, write_timeout=1)
            time.sleep(2.0)  # margen por si la placa se reinicia al abrir el puerto
            self.port = port
            self.status = f"Conectado ({port})"
            logging.info("Serial OK en %s", port)
            return True
        except Exception as e:
            logging.warning("Fallo abriendo %s: %r", port, e)
            self.status = f"No pude abrir {port}"
            self.ser = None
            return False

    def send(self, rgb, hold=False):
        if not self.ser:
            return False
        r, g, b = (max(0, min(255, int(v))) for v in rgb)
        try:
            self.ser.write(bytes([HDR_HOLD if hold else HDR_STREAM, r, g, b]))
            return True
        except Exception as e:
            logging.warning("Se cayó el serial: %r", e)
            self.close()
            self.status = "Desconectado (reintentando)"
            return False

    def set_port(self, port_setting):
        if port_setting != self.port_setting:
            self.port_setting = port_setting
            self.close()
            self._next_try = 0.0

    def close(self):
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        self.ser = None
        self.port = None
