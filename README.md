# UlisesGlow

UlisesGlow es un sistema Ambilight para PC basado en **ESP32**.  
Captura el color de la pantalla de la computadora y lo envía por puerto serie a una tira LED RGB, logrando iluminación ambiental sincronizada con la imagen.

UlisesGlow/
├── pc/ → Software de Windows (Python + Tray + Installer)
├── esp32/ → Firmware del ESP32
└── README.md → Este archivo

## 💻 PC (Windows)
La carpeta `pc/` contiene:
- El programa que corre en segundo plano (bandeja del sistema)
- El script para generar el `.exe` con PyInstaller
- El instalador con Inno Setup

El software:
- Captura una franja superior de la pantalla
- Calcula el color promedio
- Envía los valores RGB al ESP32 por serial

## 🔌 ESP32
La carpeta `esp32/` contiene:
- El firmware que recibe los datos RGB
- Controla una tira LED RGB **no direccionable** (12 V) mediante PWM

## 📦 Instalador
El instalador de Windows (`UlisesGlow_Setup.exe`) **no está en el repositorio**.

👉 Se distribuye desde **GitHub Releases**, que es la forma correcta de publicar binarios.

## 🚀 Estado del proyecto
- Funcional
- Uso diario
- Pensado para ser portable a otras PCs

## 👤 Autor
Ulises Agustin Rodriguez
Proyecto personal


