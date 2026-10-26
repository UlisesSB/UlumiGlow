# Compilar y publicar

[← Volver al README](../README.md) · [English](building.md)

Cómo pasar del código fuente a un instalador listo para subir a GitHub Releases.

## Requisitos

- Windows 10 u 11 (64 bits)
- [Python](https://www.python.org/downloads/) 3.10 o superior (marcá *Add python.exe to PATH* al instalarlo)
- [Inno Setup](https://jrsoftware.org/isdl.php) 6.3 o superior
- [PlatformIO](https://platformio.org/) (solo para el firmware)

## 1. Probar desde el código

```powershell
cd app
pip install -r requirements.txt
python main.py
```

`python main.py --tray` arranca directo en la bandeja, igual que cuando se inicia con Windows.

## 2. Generar el programa

Hacé doble clic en `app\build.bat` (o ejecutalo desde una terminal). Instala lo necesario, corre PyInstaller y deja el programa en:

```
app\dist\UlumiGlow\UlumiGlow.exe
```

Antes de seguir, abrí ese `.exe` y comprobá que funcione.

## 3. Generar el instalador

1. Abrí `app\installer\UlumiGlow.iss` con Inno Setup.
2. Si cambiaste de versión, actualizá `#define AppVersion` al principio del archivo (y `VERSION` en `app\ulumiglow\__init__.py`).
3. Compilá con **Build → Compile** (`Ctrl+F9`).

El instalador queda en `app\dist\UlumiGlow_Setup_2.0.0.exe`. Lo que hace:

- Instala para el usuario actual, sin pedir permisos de administrador.
- Ofrece **Iniciar UlumiGlow con Windows** (marcado por defecto): crea un acceso directo en la carpeta de inicio que abre la app con `--tray`.
- Ofrece un acceso directo en el escritorio (desmarcado por defecto).
- Al desinstalar, cierra la app si está abierta.

## 4. Publicar la versión en GitHub

1. Subí los cambios y creá una etiqueta con la versión, por ejemplo `v2.0.0`.
2. En GitHub, entrá a **Releases → Draft a new release**, elegí la etiqueta y pegá las notas de [CHANGELOG.md](../CHANGELOG.md).
3. Adjuntá `UlumiGlow_Setup_2.0.0.exe` y publicá.

> Los `.exe` no se suben al repositorio (están en `.gitignore`): solo van en Releases.

### Vista previa al compartir el repositorio

En **Settings → General → Social preview** del repositorio podés subir `assets/banner/social-preview.png` para que el enlace se vea con el banner al compartirlo.

## Firmware

```powershell
cd firmware
pio run -t upload      # compila y carga
pio device monitor     # monitor serie (115200)
```

La plataforma está fijada en `espressif32 @ ^6.9.0` (core Arduino 2.0.x), que es la que tiene `ledcSetup()` y `ledcAttachPin()`.

## Si venís de UlisesGlow 1.x

1. Desinstalá **UlisesGlow** desde *Configuración → Aplicaciones*.
2. La v1 intentaba crear una tarea programada llamada `UlisesGlow`. Si quedó, borrala desde una terminal **como administrador**:
   ```powershell
   schtasks /Delete /TN "UlisesGlow" /F
   ```
3. Cargá el firmware nuevo en el ESP32. Es necesario: con el anterior, la app nueva no puede usar el color fijo ni apagar la tira al pausar.
4. Instalá UlumiGlow.
