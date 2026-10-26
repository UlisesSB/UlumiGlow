# Building and releasing

[← Back to the README](../README.en.md) · [Español](compilar.md)

How to go from source code to an installer ready to upload to GitHub Releases.

## Requirements

- Windows 10 or 11 (64-bit)
- [Python](https://www.python.org/downloads/) 3.10 or newer (tick *Add python.exe to PATH* when installing)
- [Inno Setup](https://jrsoftware.org/isdl.php) 6.3 or newer
- [PlatformIO](https://platformio.org/) (firmware only)

## 1. Run from source

```powershell
cd app
pip install -r requirements.txt
python main.py
```

`python main.py --tray` starts straight in the tray, just like when it starts with Windows.

## 2. Build the app

Double-click `app\build.bat` (or run it from a terminal). It installs what is needed, runs PyInstaller and leaves the app in:

```
app\dist\UlumiGlow\UlumiGlow.exe
```

Open that `.exe` and check that it works before going on.

## 3. Build the installer

1. Open `app\installer\UlumiGlow.iss` in Inno Setup.
2. If the version changed, update `#define AppVersion` at the top of the file (and `VERSION` in `app\ulumiglow\__init__.py`).
3. Compile with **Build → Compile** (`Ctrl+F9`).

The installer ends up in `app\dist\UlumiGlow_Setup_2.0.0.exe`. It:

- Installs for the current user, without asking for administrator rights.
- Offers **Start UlumiGlow with Windows** (checked by default): it adds a startup-folder shortcut that runs the app with `--tray`.
- Offers a desktop shortcut (unchecked by default).
- Closes the app, if running, before uninstalling.

## 4. Publish the release on GitHub

1. Push your changes and create a version tag, for example `v2.0.0`.
2. On GitHub, go to **Releases → Draft a new release**, pick the tag and paste the notes from [CHANGELOG.md](../CHANGELOG.md).
3. Attach `UlumiGlow_Setup_2.0.0.exe` and publish.

> `.exe` files are not committed to the repository (they are in `.gitignore`): they only go in Releases.

### Link preview

Under the repository's **Settings → General → Social preview** you can upload `assets/banner/social-preview.png` so shared links show the banner.

## Firmware

```powershell
cd firmware
pio run -t upload      # build and flash
pio device monitor     # serial monitor (115200)
```

The platform is pinned to `espressif32 @ ^6.9.0` (Arduino core 2.0.x), which provides `ledcSetup()` and `ledcAttachPin()`.

## Upgrading from UlisesGlow 1.x

1. Uninstall **UlisesGlow** from *Settings → Apps*.
2. Version 1 tried to create a scheduled task named `UlisesGlow`. If it is still there, remove it from a terminal **run as administrator**:
   ```powershell
   schtasks /Delete /TN "UlisesGlow" /F
   ```
3. Flash the new firmware to the ESP32. This is required: with the old one, the new app cannot use solid color or switch the strip off when paused.
4. Install UlumiGlow.
