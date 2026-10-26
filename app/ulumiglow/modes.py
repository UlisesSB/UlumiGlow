"""Modos de iluminación.

Cada modo expone:
    interval  segundos entre envíos
    hold      True si el color debe quedar fijo en el ESP32 (paquete 0xAB)
    color()   devuelve (r, g, b) en 0..255, antes de curva y brillo
    close()   libera recursos
"""

import logging
import time

import numpy as np

from .color import hex_to_rgb, hsv


class Ambilight:
    """Promedia el color de una zona de la pantalla."""

    interval = 1 / 20
    hold = False
    DOWNSAMPLE = 6   # toma 1 de cada 6 píxeles por eje
    SMOOTH = 0.35    # 0..1, más alto = reacciona más rápido

    def __init__(self, cfg):
        self.cfg = cfg
        self._sct = None
        self._rgb = np.zeros(3)

    def region(self, monitors):
        idx = self.cfg["monitor"]
        mon = monitors[idx] if 1 <= idx < len(monitors) else monitors[1]
        z = self.cfg["zone"]
        x = min(max(z["x"], 0.0), 0.99)
        y = min(max(z["y"], 0.0), 0.99)
        w = min(max(z["w"], 0.01), 1.0 - x)
        h = min(max(z["h"], 0.01), 1.0 - y)
        left, top = round(x * mon["width"]), round(y * mon["height"])
        return {
            "left": mon["left"] + left,
            "top": mon["top"] + top,
            "width": max(1, min(round(w * mon["width"]), mon["width"] - left)),
            "height": max(1, min(round(h * mon["height"]), mon["height"] - top)),
        }

    def color(self):
        if self._sct is None:
            import mss  # se crea en el hilo que lo usa (requisito de mss en Windows)
            self._sct = mss.mss()
        img = np.asarray(self._sct.grab(self.region(self._sct.monitors)))
        img = img[::self.DOWNSAMPLE, ::self.DOWNSAMPLE, :3]   # BGRA -> BGR
        b, g, r = img.reshape(-1, 3).mean(axis=0)
        self._rgb += self.SMOOTH * (np.array([r, g, b]) - self._rgb)
        return tuple(self._rgb)

    def close(self):
        if self._sct:
            self._sct.close()
            self._sct = None


class Fixed:
    """Color elegido a mano, como un control remoto común."""

    interval = 1.0   # reenvía cada segundo por si el ESP32 se reconectó
    hold = True

    def __init__(self, cfg):
        self.cfg = cfg

    def color(self):
        return hex_to_rgb(self.cfg["fixed_color"])

    def close(self):
        pass


class Audio:
    """Reacciona al sonido de la PC (lo que suena por los parlantes).

    Graves -> pulso de brillo y saltos de color en cada golpe.
    Medios -> sostienen el brillo.
    Agudos -> aceleran el giro del color y lo blanquean un poco.
    """

    interval = 1 / 40
    hold = False
    BANDS = ((20, 150), (150, 2000), (2000, 10000))   # Hz: graves, medios, agudos
    PEAK_FLOOR = 0.2      # evita que el ruido de fondo se amplifique
    PEAK_DECAY = 0.995    # la normalización se adapta al volumen en ~4 s
    RELEASE = 0.90        # qué tan rápido baja el brillo después de un golpe
    KICK = 0.85           # umbral de "golpe" de graves

    def __init__(self, cfg):
        self.cfg = cfg
        self._pa = self._stream = self._chunk = None
        self._channels, self._rate = 2, 48000
        self._retry_at = 0.0
        self._peaks = [self.PEAK_FLOOR] * 3
        self._env = 0.0
        self._hue = 0.6
        self._prev_bass = 0.0

    # --- captura (WASAPI loopback) ---
    def _open(self):
        import pyaudiowpatch as pyaudio
        self._pa = pyaudio.PyAudio()
        dev = self._pa.get_default_wasapi_loopback()
        self._channels = dev["maxInputChannels"]
        self._rate = int(dev["defaultSampleRate"])

        def callback(data, frames, info, status):
            self._chunk = data
            return (None, pyaudio.paContinue)

        self._stream = self._pa.open(
            format=pyaudio.paFloat32, channels=self._channels, rate=self._rate,
            input=True, input_device_index=dev["index"],
            frames_per_buffer=1024, stream_callback=callback)
        logging.info("Audio: capturando '%s'", dev["name"])

    def bands(self, samples):
        """Energía promedio por banda de un bloque de audio mono."""
        spec = np.abs(np.fft.rfft(samples * np.hanning(len(samples))))
        freqs = np.fft.rfftfreq(len(samples), 1 / self._rate)
        return [float(spec[(freqs >= lo) & (freqs < hi)].mean()) for lo, hi in self.BANDS]

    def color(self):
        if self._stream is None and time.monotonic() >= self._retry_at:
            try:
                self._open()
            except Exception as e:
                logging.warning("No pude abrir el audio: %r", e)
                self.close()
                self._retry_at = time.monotonic() + 5

        data, self._chunk = self._chunk, None
        if data:
            x = np.frombuffer(data, np.float32).reshape(-1, self._channels).mean(axis=1)
            energy = self.bands(x)
        else:
            energy = [0.0, 0.0, 0.0]   # sin sonido nuevo
        return self.react(energy)

    def react(self, energy):
        """Convierte la energía de cada banda en un color."""
        levels = []
        for i, e in enumerate(energy):
            self._peaks[i] = max(e, self._peaks[i] * self.PEAK_DECAY, self.PEAK_FLOOR)
            levels.append(e / self._peaks[i])
        bass, mid, high = levels

        target = max(bass, 0.6 * mid)
        self._env = target if target > self._env else self._env * self.RELEASE
        if bass > self.KICK >= self._prev_bass:
            self._hue += 0.18
        self._prev_bass = bass
        self._hue += 0.002 + 0.02 * high

        return hsv(self._hue, 1.0 - 0.35 * high, 0.06 + 0.94 * self._env)

    def close(self):
        try:
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
            if self._pa:
                self._pa.terminate()
        except Exception:
            pass
        self._pa = self._stream = self._chunk = None


MODES = {"ambilight": Ambilight, "fixed": Fixed, "audio": Audio}
