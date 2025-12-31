import threading
import time
import sys
import os
import traceback

import numpy as np
import mss
import serial
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import re
import serial.tools.list_ports

# ================= CONFIG =================

# VID común de Espressif (303A). PID puede variar según modo/driver.
ESPRESSIF_VIDS = {"303A"}

KEYWORDS = [
    "usb serial/jtag",
    "esp32",
    "cp210",      # Silicon Labs CP210x
    "ch340",      # WCH CH340
    "silicon labs",
    "wch"
]

def autodetect_esp32_port():
    ports = list(serial.tools.list_ports.comports())

    # 1) Preferencia: VID Espressif (más seguro si usás USB Serial/JTAG del C3)
    for p in ports:
        hwid = (p.hwid or "").upper()
        m = re.search(r"VID:PID=([0-9A-F]{4}):([0-9A-F]{4})", hwid)
        if m:
            vid = m.group(1)
            if vid in ESPRESSIF_VIDS:
                return p.device

    # 2) Fallback: keywords en description/hwid
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if any(k in desc or k in hwid for k in KEYWORDS):
            return p.device

    return None

PORT = autodetect_esp32_port()  # devuelve "COM8", etc. o None


BAUD = 115200

FPS = 20
DOWNSAMPLE = 6
SMOOTH = 0.35
GAMMA = 2.2
TOP_PERCENT = 0.10

ICON_FILE = "ulisesglow_icon.png"
UI_REFRESH_SEC = 0.5
# =========================================

running = False
exit_app = False
ser = None
last_rgb = (0, 0, 0)
status_msg = "OK"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "tray_debug.log")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def gamma_correct(x):
    xf = (x / 255.0) ** (1.0 / GAMMA)
    v = int(xf * 255.0)
    return 0 if v < 0 else 255 if v > 255 else v

def make_fallback_icon():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill=(0, 200, 255, 255))
    return img

def load_base_icon():
    path = os.path.join(BASE_DIR, ICON_FILE)
    try:
        return Image.open(path).convert("RGBA")
    except Exception as e:
        log(f"WARNING: no pude abrir PNG '{path}': {repr(e)}")
        return make_fallback_icon()

def icon_with_badge(base_img, is_on: bool):
    img = base_img.copy()
    d = ImageDraw.Draw(img)
    badge_color = (0, 220, 120, 255) if is_on else (220, 60, 60, 255)
    d.ellipse((img.width - 18, 2, img.width - 2, 18), fill=badge_color)
    return img

def ambilight_loop():
    global running, exit_app, ser, last_rgb, status_msg, PORT
    try:
        log("HILO: iniciando")

        # Intento abrir el COM. Si no hay ESP32, reintenta cada 2s.
        while not exit_app:
            if PORT is None:
                status_msg = "ESP32 no detectado (conecta y espero)"
                time.sleep(2.0)
                PORT = autodetect_esp32_port()
                continue

            # Si ya hay PORT, intento abrirlo
            try:
                status_msg = f"Abriendo {PORT}..."
                ser = serial.Serial(PORT, BAUD, timeout=0)
                time.sleep(2.0)
                status_msg = f"COM OK ({PORT})"
                log(f"Serial OK en {PORT}")
                break
            except Exception as e:
                # Puede haber cambiado el COM o estar ocupado
                log(f"Fallo abriendo {PORT}: {repr(e)}")
                status_msg = f"Fallo {PORT} (reintento)"
                PORT = None
                time.sleep(2.0)

        if exit_app:
            return

        with mss.mss() as sct:
            screen = sct.monitors[1]
            top_h = max(1, int(screen["height"] * TOP_PERCENT))
            region = {
                "top": screen["top"],
                "left": screen["left"],
                "width": screen["width"],
                "height": top_h
            }
            log(f"Region: {region}")

            r_f = g_f = b_f = 0.0
            dt = 1.0 / FPS

            while not exit_app:
                if running and ser:
                    img = np.array(sct.grab(region))          # BGRA
                    img = img[::DOWNSAMPLE, ::DOWNSAMPLE, :3] # BGR

                    b = img[:, :, 0].mean()
                    g = img[:, :, 1].mean()
                    r = img[:, :, 2].mean()

                    r_f = (1 - SMOOTH) * r_f + SMOOTH * r
                    g_f = (1 - SMOOTH) * g_f + SMOOTH * g
                    b_f = (1 - SMOOTH) * b_f + SMOOTH * b

                    R = gamma_correct(r_f)
                    G = gamma_correct(g_f)
                    B = gamma_correct(b_f)

                    last_rgb = (R, G, B)
                    try:
                        ser.write(bytes([0xAA, R, G, B]))
                    except Exception as e:
                        log(f"Serial write fallo: {repr(e)}")
                        status_msg = "Serial caido (reconecto)"
                        try:
                            ser.close()
                        except:
                            pass
                        ser = None
                        PORT = None

                time.sleep(dt)

        log("HILO: saliendo limpio")

    except Exception:
        status_msg = "ERROR (ver log)"
        log("ERROR en hilo ambilight_loop():")
        log(traceback.format_exc())


def update_ui(icon, base_icon):
    icon.title = "Ambilight ON" if running else "Ambilight OFF"
    icon.icon = icon_with_badge(base_icon, running)
    icon.update_menu()

def on_toggle(icon, _item, base_icon):
    global running
    running = not running
    log(f"Toggle -> {'ON' if running else 'OFF'}")
    update_ui(icon, base_icon)

def on_exit(icon, _item):
    global exit_app, running, ser
    log("Salir")
    running = False
    exit_app = True
    try:
        if ser:
            ser.close()
    except:
        pass
    icon.stop()
    sys.exit(0)

def menu_factory(base_icon):
    return pystray.Menu(
        item(lambda _ : f"Estado: {'CORRIENDO' if running else 'PAUSADO'}", None, enabled=False),
        item(lambda _ : f"RGB: {last_rgb[0]:03d}, {last_rgb[1]:03d}, {last_rgb[2]:03d}", None, enabled=False),
        item(lambda _ : f"COM: {PORT} | {status_msg}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        item(
            "Activar / Pausar",
            lambda icon, it: on_toggle(icon, it, base_icon),
            default=True,
            checked=lambda _ : running
        ),
        item("Salir", on_exit),
    )


def ui_refresh_loop(icon, base_icon):
    while not exit_app:
        try:
            update_ui(icon, base_icon)
        except:
            pass
        time.sleep(UI_REFRESH_SEC)

def main():
    log("=== INICIO ambilight_tray.py ===")
    base_icon = load_base_icon()

    # Hilo de trabajo (captura + envío)
    threading.Thread(target=ambilight_loop, daemon=True).start()

    # Icono tray
    icon = pystray.Icon(
        "Ambilight",
        icon_with_badge(base_icon, False),
        "Ambilight OFF",
        menu_factory(base_icon)
    )

    # Refresh UI
    threading.Thread(target=ui_refresh_loop, args=(icon, base_icon), daemon=True).start()

    log("Icono tray run()")
    icon.run()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("ERROR en main():")
        log(traceback.format_exc())
        raise
