# Changelog

Todos los cambios importantes del proyecto. Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [versionado semántico](https://semver.org/lang/es/).

## [2.0.0] - 2026-10-26

El proyecto pasa a llamarse **UlumiGlow** (antes *UlisesGlow*).

### Agregado
- Ventana de configuración nueva con estilo *liquid glass* azul.
- Intro animada al abrir el programa (no aparece cuando arranca con Windows).
- **Mapa de zona** para Ambilight: presets Arriba, Abajo, Izquierda, Derecha y Toda la pantalla, más una zona personalizada que se marca arrastrando sobre una captura. Se puede elegir el grosor de la franja y el monitor.
- **Modo Color fijo**: el color queda puesto en el ESP32 aunque se cierre el programa.
- **Modo Audio**: la tira reacciona al sonido de la PC (graves, medios y agudos).
- Control de brillo general y selector de puerto (automático o manual).
- Selector de curva de color: **LED** (`x^2.2`, nueva por defecto) o **Clásica** (la de la v1) para comparar.
- Menú de la bandeja con encendido, cambio de modo, configuración y estado del ESP32.
- Firmware: paquete `0xAB` para color fijo y apagado automático si dejan de llegar datos en los modos en vivo.
- Se evita abrir el programa dos veces: la segunda vez solo muestra la ventana.
- Logo redibujado en vector (4096 px), ícono nuevo, banners y diagrama de conexión.
- Licencia MIT, README en español e inglés, guías de armado y compilación.

### Corregido
- Si se desconectaba el ESP32, el programa no volvía a conectarse hasta reiniciarlo.
- Al pausar o salir, la tira quedaba prendida con el último color.
- El inicio automático del instalador apuntaba a una ruta inválida (`{app}` sin expandir).
- El log crecía sin límite y se guardaba en la carpeta del programa. Ahora vive en `%APPDATA%\UlumiGlow` con tamaño acotado.
- La documentación del firmware indicaba pines equivocados (son GPIO 4, 5 y 6).
- `platformio.ini` no fijaba la versión de la plataforma; con el core 3.x el firmware no compilaba.

### Cambiado
- El instalador ya no pide permisos de administrador y el inicio con Windows es opcional.
- La app se distribuye como carpeta (PyInstaller *onedir*), que arranca más rápido que un único `.exe`.

## [1.0.0] - 2025

Primera versión pública como **UlisesGlow**: captura de la franja superior de la pantalla, ícono en la bandeja y firmware para ESP32-C3.
