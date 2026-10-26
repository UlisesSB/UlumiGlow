# Assembling the circuit

[← Back to the README](../README.en.md) · [Español](armado.md)

This guide explains how to wire the ESP32-C3, the MOSFETs and the LED strip. It is a small circuit that fits on a breadboard.

<p align="center"><img src="img/circuito.svg" alt="Wiring diagram" width="100%"></p>

## Before you start

- The strip must be a **12 V non-addressable RGB** strip with 4 wires or pads: `+12V`, `R`, `G` and `B`. "Smart" strips with a single data line (WS2812, NeoPixel) **will not work** with this circuit.
- Always keep the PC and the power supply **off** while wiring.
- The ESP32 **never** powers the strip: it only drives the MOSFETs. The strip's current comes from the 12 V supply.

## Parts

| Ref. | Part | Qty |
|---|---|:---:|
| U1 | ESP32-C3 SuperMini | 1 |
| Q1, Q2, Q3 | IRFZ44N N-channel MOSFET (or IRLZ44N / IRLB8721) | 3 |
| R1, R2, R3 | 220 Ω resistor (gate) | 3 |
| R4, R5, R6 | 10 kΩ resistor (pull-down) | 3 |
| – | 12 V non-addressable RGB LED strip | 1 |
| – | 12 V power supply (PC ATX PSU or external) | 1 |

### MOSFET pinout

Looking at the IRFZ44N from the front (text facing you, legs down), from left to right:

| Pin | Name | Connects to |
|:---:|---|---|
| 1 | **G** (gate) | ESP32 GPIO through 220 Ω, and to ground through 10 kΩ |
| 2 | **D** (drain) | The strip's R, G or B wire |
| 3 | **S** (source) | Ground (GND) |

> The metal tab on the back is connected to the drain. If you use heatsinks, make sure they do not touch each other.

## Step by step

1. **Common ground.** Make a GND rail on the breadboard and connect the ESP32's `GND` pin, the **source** of all three MOSFETs and the black (GND) wire of the 12 V supply to it. The circuit will not work without this common ground.
2. **Gates.** For each channel, put a **220 Ω** resistor between the GPIO and the MOSFET gate:
   - GPIO 4 → Q1 (red)
   - GPIO 5 → Q2 (green)
   - GPIO 6 → Q3 (blue)
3. **Pull-downs.** Put a **10 kΩ** resistor between each MOSFET gate and GND. This keeps the strip off while the ESP32 boots or if it gets disconnected.
4. **Drains to the strip.** Connect Q1's drain to the strip's `R` wire, Q2's to `G` and Q3's to `B`.
5. **12 V to the strip.** Connect the strip's `+12V` to the yellow (12 V) wire of the supply.
6. **USB.** Connect the ESP32 to the PC with a USB-C **data** cable (some cables only charge).

### Getting 12 V from the ATX PSU

If you use the PC's power supply, you can take 12 V from a spare Molex or SATA connector:

| Wire color | Voltage |
|---|---|
| Yellow | +12 V |
| Black | GND |
| Red | +5 V (unused) |

Using an adapter or a female Molex connector is cleaner than cutting the PSU's wires.

## Flashing the firmware

1. Install [VS Code](https://code.visualstudio.com/) and the **PlatformIO IDE** extension.
2. Open the repository's `firmware/` folder.
3. Plug in the ESP32-C3 and click **Upload** (the arrow in the bottom bar), or run `pio run -t upload`.
4. To check it, open the **Serial Monitor**: after resetting the board you should see `UlumiGlow listo`.

> If the board does not show up as a port, hold the **BOOT** button, press **RST** (or unplug and replug the USB) and release BOOT. Reset the board after flashing.

## Firmware settings

In [`firmware/src/main.cpp`](../firmware/src/main.cpp):

| Constant | Value | Purpose |
|---|---|---|
| `PIN_R`, `PIN_G`, `PIN_B` | 4, 5, 6 | Pin for each color. If colors come out swapped you can fix it here |
| `BRIGHT_LIMIT` | 160 | Maximum brightness (0-255). With logic-level MOSFETs it can go up to 255 |
| `STREAM_TIMEOUT_MS` | 3000 | Time without data (ms) before turning the strip off in Ambilight and Audio |

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| The strip does not light at all | Missing common ground or 12 V | Make sure the ESP32 GND, the sources and the PSU GND are joined |
| One color is always on | Floating gate or miswired MOSFET | Check the 10 kΩ resistor and the G-D-S order of that MOSFET |
| Colors are swapped (red instead of blue, etc.) | R/G/B wires crossed | Swap the wires at the strip or the pins in the firmware |
| The MOSFETs get hot | IRFZ44N with 3.3 V on the gate | Keep `BRIGHT_LIMIT` at 160 or lower, add heatsinks or switch to IRLZ44N / IRLB8721 |
| The app says "ESP32 no detectado" | Charge-only cable or firmware not flashed | Try another USB cable and pick the port manually under *Puerto del ESP32* |
| The strip flickers or misbehaves | Weak supply or long, thin wires | Use thicker wires for 12 V and keep gate wires short |
