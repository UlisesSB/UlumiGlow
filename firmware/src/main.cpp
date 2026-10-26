/*
 * UlumiGlow - Firmware para ESP32-C3
 * Copyright (c) 2025-2026 Ulises Agustin Rodriguez - Licencia MIT
 * https://github.com/UlisesSB/UlumiGlow
 *
 * Recibe colores por USB (puerto serie) y los saca por PWM hacia tres
 * MOSFETs que manejan una tira LED RGB comun (no direccionable) de 12 V.
 *
 * Protocolo: paquetes de 4 bytes a 115200 baudios.
 *   0xAA R G B  -> color "en vivo" (modos Ambilight y Audio).
 *                  Si dejan de llegar paquetes durante STREAM_TIMEOUT_MS
 *                  (PC suspendida, programa cerrado), la tira se apaga sola.
 *   0xAB R G B  -> color fijo. Queda puesto aunque la PC deje de enviar.
 */

#include <Arduino.h>

// ---------- Pines y PWM ----------
#define PIN_R 4
#define PIN_G 5
#define PIN_B 6

#define CH_R 0
#define CH_G 1
#define CH_B 2

#define PWM_FREQ 5000   // Hz
#define PWM_RES  8      // bits -> valores 0..255

// ---------- Ajustes ----------
// Brillo maximo (0-255). Los IRFZ44N no son de nivel logico: con 3,3 V en
// el gate no conducen del todo y calientan. 160 (~63 %) los mantiene frescos.
// Con MOSFETs de nivel logico (IRLZ44N, IRLB8721) se puede subir a 255.
static const uint8_t  BRIGHT_LIMIT      = 160;
static const uint32_t STREAM_TIMEOUT_MS = 3000;

static const uint8_t HDR_STREAM = 0xAA;
static const uint8_t HDR_HOLD   = 0xAB;

static bool     streaming    = false;  // true si el ultimo paquete fue 0xAA
static uint32_t lastPacketMs = 0;

// Escala 0..255 al rango 0..BRIGHT_LIMIT (con redondeo).
static inline uint8_t scale_limit(uint8_t v) {
  return (uint16_t(v) * BRIGHT_LIMIT + 127) / 255;
}

static void setColor(uint8_t r, uint8_t g, uint8_t b) {
  ledcWrite(CH_R, scale_limit(r));
  ledcWrite(CH_G, scale_limit(g));
  ledcWrite(CH_B, scale_limit(b));
}

void setup() {
  Serial.begin(115200);
  delay(300);

  ledcSetup(CH_R, PWM_FREQ, PWM_RES);
  ledcSetup(CH_G, PWM_FREQ, PWM_RES);
  ledcSetup(CH_B, PWM_FREQ, PWM_RES);

  ledcAttachPin(PIN_R, CH_R);
  ledcAttachPin(PIN_G, CH_G);
  ledcAttachPin(PIN_B, CH_B);

  setColor(0, 0, 0);

  Serial.println("UlumiGlow listo: 0xAA|0xAB R G B");
}

void loop() {
  // Busca un byte de inicio valido y despues lee los 3 bytes de color.
  while (Serial.available() >= 4) {
    int header = Serial.read();
    if (header != HDR_STREAM && header != HDR_HOLD) continue;  // resincroniza

    uint8_t r = (uint8_t)Serial.read();
    uint8_t g = (uint8_t)Serial.read();
    uint8_t b = (uint8_t)Serial.read();

    setColor(r, g, b);
    streaming    = (header == HDR_STREAM);
    lastPacketMs = millis();
  }

  // Apagado automatico: solo para el color en vivo, nunca para el fijo.
  if (streaming && millis() - lastPacketMs > STREAM_TIMEOUT_MS) {
    setColor(0, 0, 0);
    streaming = false;
  }
}
