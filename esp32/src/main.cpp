#include <Arduino.h>

#define PIN_R 4
#define PIN_G 5
#define PIN_B 6

#define CH_R 0
#define CH_G 1
#define CH_B 2

#define PWM_FREQ 5000
#define PWM_RES  8   // 0..255

// Limitá brillo por tus IRFZ44N (ajustalo luego: 80, 120, 160...)
static const uint8_t BRIGHT_LIMIT = 160;

static inline uint8_t scale_limit(uint8_t v) {
  return (uint16_t(v) * BRIGHT_LIMIT + 127) / 255;
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

  ledcWrite(CH_R, 0);
  ledcWrite(CH_G, 0);
  ledcWrite(CH_B, 0);

  Serial.println("ESP32-C3 listo para recibir 0xAA R G B");
}

void loop() {
  // Buscamos el byte de inicio 0xAA, luego 3 bytes RGB
  while (Serial.available() >= 4) {
    int b = Serial.read();
    if (b != 0xAA) continue;

    uint8_t r = (uint8_t)Serial.read();
    uint8_t g = (uint8_t)Serial.read();
    uint8_t b2 = (uint8_t)Serial.read();

    r = scale_limit(r);
    g = scale_limit(g);
    b2 = scale_limit(b2);

    ledcWrite(CH_R, r);
    ledcWrite(CH_G, g);
    ledcWrite(CH_B, b2);
  }
}
