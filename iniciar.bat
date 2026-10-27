@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist "%~dp0gui.py" (
  echo Falta gui.py en esta carpeta.
  pause
  exit /b 1
)

if not exist "%~dp0.venv\Scripts\pythonw.exe" (
  echo No hay entorno virtual. Ejecuto instalar.ps1 ...
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
  if errorlevel 1 (
    echo Fallo la instalacion.
    pause
    exit /b 1
  )
)

start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0gui.py"
exit /b 0
