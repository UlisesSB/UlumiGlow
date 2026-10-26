@echo off
REM ===================================================================
REM  UlumiGlow - genera el programa para Windows con PyInstaller
REM  Resultado: dist\UlumiGlow\UlumiGlow.exe  (carpeta lista para el instalador)
REM ===================================================================
cd /d "%~dp0"

python -m pip install -r requirements.txt pyinstaller || goto :error

python -m PyInstaller --noconfirm --clean --windowed ^
  --name UlumiGlow ^
  --icon assets\ulumiglow.ico ^
  --add-data "assets;assets" ^
  --add-data "ulumiglow\ui\web;ulumiglow\ui\web" ^
  --hidden-import pystray._win32 ^
  main.py || goto :error

echo.
echo Listo: dist\UlumiGlow\UlumiGlow.exe
echo Ahora abri installer\UlumiGlow.iss con Inno Setup y compila (Ctrl+F9).
exit /b 0

:error
echo.
echo Hubo un error. Revisa los mensajes de arriba.
exit /b 1
