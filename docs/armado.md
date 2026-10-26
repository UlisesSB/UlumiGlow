# Armado del circuito

[← Volver al README](../README.md) · [English](assembly.md)

Esta guía explica cómo conectar el ESP32-C3, los MOSFETs y la tira LED. Es un circuito chico que entra en una protoboard.

<p align="center"><img src="img/circuito.svg" alt="Esquema de conexión" width="100%"></p>

## Antes de empezar

- La tira tiene que ser **RGB de 12 V no direccionable**, con 4 cables o pines: `+12V`, `R`, `G` y `B`. Las tiras "inteligentes" de un solo cable de datos (WS2812, NeoPixel) **no sirven** para este circuito.
- Trabajá siempre con la PC y la fuente **apagadas** mientras conectás cables.
- El ESP32 **nunca** alimenta la tira: solo le da la orden a los MOSFETs. La corriente de la tira sale de la fuente de 12 V.

## Componentes

| Ref. | Componente | Cant. |
|---|---|:---:|
| U1 | ESP32-C3 SuperMini | 1 |
| Q1, Q2, Q3 | MOSFET de canal N IRFZ44N (o IRLZ44N / IRLB8721) | 3 |
| R1, R2, R3 | Resistencia de 220 Ω (gate) | 3 |
| R4, R5, R6 | Resistencia de 10 kΩ (pull-down) | 3 |
| – | Tira LED RGB 12 V no direccionable | 1 |
| – | Fuente de 12 V (ATX de la PC o externa) | 1 |

### Patas del MOSFET

Mirando el IRFZ44N de frente (con el texto hacia vos y las patas hacia abajo), de izquierda a derecha:

| Pata | Nombre | Se conecta a |
|:---:|---|---|
| 1 | **G** (gate) | GPIO del ESP32 a través de 220 Ω, y a masa a través de 10 kΩ |
| 2 | **D** (drain) | Cable R, G o B de la tira |
| 3 | **S** (source) | Masa (GND) |

> La parte metálica de atrás (la aleta) está conectada al drain. Si usás disipadores, que no se toquen entre MOSFETs.

## Paso a paso

1. **Masa común.** Armá una línea de GND en la protoboard y conectá ahí el pin `GND` del ESP32, el **source** de los tres MOSFETs y el cable negro (GND) de la fuente de 12 V. Sin esta masa común el circuito no funciona.
2. **Gates.** Para cada canal, poné una resistencia de **220 Ω** entre el GPIO y el gate del MOSFET:
   - GPIO 4 → Q1 (rojo)
   - GPIO 5 → Q2 (verde)
   - GPIO 6 → Q3 (azul)
3. **Pull-downs.** Poné una resistencia de **10 kΩ** entre el gate de cada MOSFET y GND. Esto mantiene la tira apagada mientras el ESP32 arranca o si se desconecta.
4. **Drains a la tira.** Conectá el drain de Q1 al cable `R` de la tira, el de Q2 al `G` y el de Q3 al `B`.
5. **12 V a la tira.** Conectá el `+12V` de la tira al cable amarillo (12 V) de la fuente.
6. **USB.** Conectá el ESP32 a la PC con un cable USB-C **de datos** (algunos cables solo cargan).

### Sacar 12 V de la fuente ATX

Si usás la fuente de la PC, podés tomar los 12 V de un conector Molex o SATA que no uses:

| Color del cable | Tensión |
|---|---|
| Amarillo | +12 V |
| Negro | GND |
| Rojo | +5 V (no se usa) |

Lo más prolijo es usar un adaptador o un conector Molex hembra en lugar de cortar cables de la fuente.

## Cargar el firmware

1. Instalá [VS Code](https://code.visualstudio.com/) y la extensión **PlatformIO IDE**.
2. Abrí la carpeta `firmware/` del repositorio.
3. Conectá el ESP32-C3 y tocá **Upload** (la flecha de la barra inferior), o ejecutá `pio run -t upload`.
4. Si querés verificar, abrí el **Serial Monitor**: al reiniciar la placa tiene que aparecer `UlumiGlow listo`.

> Si la placa no aparece como puerto, mantené apretado el botón **BOOT**, tocá **RST** (o desconectá y reconectá el USB) y soltá BOOT. Después de cargar el firmware, reiniciala.

## Ajustes del firmware

En [`firmware/src/main.cpp`](../firmware/src/main.cpp):

| Constante | Valor | Para qué sirve |
|---|---|---|
| `PIN_R`, `PIN_G`, `PIN_B` | 4, 5, 6 | Pines de cada color. Si los colores salen cambiados, podés corregirlo acá |
| `BRIGHT_LIMIT` | 160 | Brillo máximo (0-255). Con MOSFETs de nivel lógico se puede subir a 255 |
| `STREAM_TIMEOUT_MS` | 3000 | Tiempo sin datos (en ms) para apagar la tira en Ambilight y Audio |

## Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| La tira no prende nada | Falta la masa común o los 12 V | Revisá que el GND del ESP32, los sources y el GND de la fuente estén unidos |
| Un color queda siempre prendido | Gate al aire o MOSFET mal conectado | Revisá la resistencia de 10 kΩ y el orden G-D-S de ese MOSFET |
| Los colores salen cambiados (rojo en vez de azul, etc.) | Cables R/G/B cruzados | Intercambiá los cables en la tira o los pines en el firmware |
| Los MOSFETs calientan | IRFZ44N con 3,3 V en el gate | Dejá `BRIGHT_LIMIT` en 160 o menos, agregá disipadores o cambiá a IRLZ44N / IRLB8721 |
| La app dice "ESP32 no detectado" | Cable de solo carga o firmware sin cargar | Probá otro cable USB y elegí el puerto a mano en *Puerto del ESP32* |
| La tira parpadea o hace cosas raras | Fuente floja o cables largos y finos | Usá cables más gruesos para los 12 V y acortá los del gate |
