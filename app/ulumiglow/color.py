"""Utilidades de color: curvas de brillo y conversiones."""

import colorsys

GAMMA = 2.2


def apply_curve(v, curve):
    """Corrige un canal 0..255 según la curva elegida.

    led     -> x^2.2: compensa que el LED responde lineal y el ojo no.
               Colores más saturados y oscuros más profundos.
    classic -> x^(1/2.2): la curva de la v1. Levanta los oscuros (más brillo,
               colores más lavados). Se deja para poder comparar.
    """
    x = max(0.0, min(255.0, v)) / 255.0
    if curve == "classic":
        return int(x ** (1.0 / GAMMA) * 255.0)
    return round(x ** GAMMA * 255.0)


def output(rgb, curve="led", brightness=100):
    """Color final que se envía al ESP32: curva + brillo general."""
    k = max(0, min(100, brightness)) / 100.0
    return tuple(int(apply_curve(c, curve) * k) for c in rgb)


def hex_to_rgb(value):
    value = value.lstrip("#")
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return (0, 0, 0)


def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (r * 255, g * 255, b * 255)
