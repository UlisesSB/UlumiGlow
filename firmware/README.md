# Firmware UlumiGlow (ESP32-C3)

Recibe colores por USB y los saca por PWM (GPIO 4, 5 y 6) hacia tres MOSFETs que manejan una tira LED RGB de 12 V.

```powershell
pio run -t upload      # compila y carga
pio device monitor     # monitor serie (115200)
```

| Paquete | Uso |
|---|---|
| `0xAA R G B` | Color en vivo. Si dejan de llegar por 3 s, la tira se apaga |
| `0xAB R G B` | Color fijo. Queda puesto |

Conexión, ajustes y solución de problemas: [docs/armado.md](../docs/armado.md) · [English](../docs/assembly.md)
