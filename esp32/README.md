# Firmware ESP32 – UlisesGlow

Este firmware corre en un **ESP32 (ESP32-C3)** y se encarga de recibir datos RGB por puerto serie y generar señales PWM para controlar una tira LED RGB no direccionable.

## 🧠 Funcionamiento general
1. El PC envía paquetes por serial
2. El ESP32 interpreta los valores RGB
3. Cada canal (R, G, B) se controla por PWM
4. La tira LED se alimenta a 12 V mediante MOSFETs externos

## 📡 Protocolo serie
- Baudrate: **115200**
- Formato del paquete:

0xAA R G B

Donde:
- `0xAA` → byte de sincronización
- `R`, `G`, `B` → valores de 0 a 255

## 📌 Pines utilizados (ejemplo)
*(ajustar si cambiás pines)*

| Canal | GPIO ESP32 |
|-----|------------|
| Rojo | GPIO 25 |
| Verde | GPIO 26 |
| Azul | GPIO 27 |

## ⚡ Hardware esperado
- ESP32-C3
- 3 MOSFETs N-channel (ej. IRFZ44N)
- Tira LED RGB 12 V (no direccionable)
- Fuente ATX o fuente 12 V externa
- Masa común entre ESP32 y fuente 12 V

## 🛠️ Compilación
Proyecto pensado para **PlatformIO**.

Archivos principales:
esp32/
├── platformio.ini
└── src/
└── main.cpp


## 📎 Notas
- La intensidad se controla por software (PWM)
- El ESP32 no alimenta la tira directamente
- Diseño pensado para ser simple y robusto

## 👤 Autor
Ulises Agustin Rodriguez
Firmware para UlisesGlow
