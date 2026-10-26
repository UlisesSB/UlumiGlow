"""UlumiGlow - punto de entrada.

    python main.py          abre con la intro animada
    python main.py --tray   arranca directo en la bandeja (lo usa el inicio de Windows)

Copyright (c) 2025-2026 Ulises Agustin Rodriguez - Licencia MIT
"""

import logging
import os
import socket
import sys
import threading
from logging.handlers import RotatingFileHandler

from ulumiglow import DATA_DIR, VERSION

INSTANCE_PORT = 47231   # puerto local para evitar dos UlumiGlow a la vez


def setup_logging():
    handler = RotatingFileHandler(os.path.join(DATA_DIR, "ulumiglow.log"),
                                  maxBytes=256_000, backupCount=1, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler],
                        format="[%(asctime)s] %(levelname)s %(message)s")


def single_instance(on_show):
    """True si somos la única instancia. Si ya hay otra, le pide que se muestre."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("127.0.0.1", INSTANCE_PORT))
    except OSError:
        try:
            socket.create_connection(("127.0.0.1", INSTANCE_PORT), timeout=1).close()
        except OSError:
            pass
        return False
    server.listen(1)

    def serve():
        while True:
            conn, _ = server.accept()
            conn.close()
            on_show()

    threading.Thread(target=serve, daemon=True, name="instance").start()
    return True


def main():
    setup_logging()
    logging.info("=== UlumiGlow %s ===", VERSION)
    start_hidden = "--tray" in sys.argv

    from ulumiglow.app import App
    app = App(show_intro=not start_hidden)
    if not single_instance(app.show_window):
        return
    app.run(start_hidden)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Error fatal")
        raise
