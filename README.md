# transcript_local

Programa para Windows que transcribe vídeo o audio a texto **en tu PC** (sin subir nada a la nube). Usa [faster-whisper](https://github.com/SYSTRAN/faster-whisper) con los modelos de OpenAI Whisper.

Arrastra un `.mp4` / `.mkv` / `.wav` / `.mp3` y te genera un Word (y, si quieres, `.txt` o `.srt`) en `Escritorio\Transcripciones`.

## Cómo usarlo

Hace falta **Python 3.10+** y **FFmpeg** una sola vez. Después basta con el acceso directo o `iniciar.bat`.

1. Instala FFmpeg si no lo tienes: `winget install Gyan.FFmpeg` (cierra y abre la terminal después)
2. En esta carpeta, abre PowerShell y ejecuta: `.\instalar.ps1`
3. Opcional: `.\crear-acceso.ps1` deja **transcript_local** en el escritorio
4. Abre `iniciar.bat` (o el acceso del escritorio), suelta el archivo y espera
5. Si quieres cambiar modelo o formatos, pulsa **Ajustes** (edita `ajustes.ini`), guarda y vuelve a abrir el programa

La primera vez descarga el modelo (unos cientos de MB). Las siguientes va más rápido.

En un vídeo de ~1 h, en CPU, el modelo `small` puede tardar del orden de 20–40 min según el PC.

## Opciones

Todo se guarda en `ajustes.ini` y se lee al abrir:

- **modelo**: `tiny` / `base` / `small` / `medium` / `large-v3` (más grande = mejor y más lento)
- **idioma**: `es` por defecto; vacío = autodetectar
- **carpeta**: dónde guardar; vacío = `Escritorio\Transcripciones`
- **formatos**: `docx`, `txt`, `srt` (separados por coma)
- **dispositivo** / **calculo**: `cpu`+`int8` por defecto; con GPU NVIDIA puedes probar `cuda`+`float16`
- **ssl_inseguro**: pon `1` solo si tu red corporativa rompe la descarga del modelo

También puedes tirar por consola:

```powershell
.\transcribir.ps1 .\reunion.mp4
.\transcribir.ps1 .\reunion.mp4 -Modelo medium -Formatos "docx,srt"
```

## Archivos

| Archivo | Para qué |
|---|---|
| `iniciar.bat` | abre la ventana (instala el entorno si falta) |
| `instalar.ps1` | crea `.venv` e instala dependencias |
| `crear-acceso.ps1` | acceso directo en el escritorio |
| `gui.py` | ventana de arrastrar / elegir archivo |
| `transcribir.py` | motor de transcripción y salida Word/txt/srt |
| `transcribir.ps1` | mismo motor desde la consola |
| `ajustes.ini` | modelo, idioma, carpeta, formatos |
| `icono-j.ico` | icono del acceso directo |
| `requirements.txt` | paquetes de Python |

## Código fuente

Para usarlo del día a día, con `iniciar.bat` basta. Solo si quieres tocar el código hace falta Python y editar `gui.py` / `transcribir.py`. El entorno virtual (`.venv`) no se sube al repo: cada máquina lo genera con `instalar.ps1`.
