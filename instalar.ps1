# Crea el entorno virtual e instala dependencias.
# Ejecutar una vez (o cuando cambie requirements.txt).
# Necesitas Python 3.10+ en el PATH.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

# Preferir 3.12/3.11/3.10 (los que mejor van con faster-whisper en Windows).
$PyExe = $null
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
foreach ($ver in @("3.12", "3.11", "3.10")) {
    $out = & py "-$ver" -c "import sys; print(sys.executable)" 2>$null
    if ($LASTEXITCODE -eq 0 -and $out) {
        $candidate = ($out | Select-Object -Last 1).ToString().Trim()
        if (Test-Path -LiteralPath $candidate) {
            $PyExe = $candidate
            break
        }
    }
}
if (-not $PyExe) {
    foreach ($c in @("python", "python3")) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd) { $PyExe = $cmd.Source; break }
    }
}
$ErrorActionPreference = $prevEap
if (-not $PyExe) {
    throw "No encuentro Python. Instálalo desde https://www.python.org/ (marca 'Add to PATH')."
}
Write-Host "Usando: $PyExe"

$Venv = Join-Path $Root ".venv"
$VenvPy = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $VenvPy)) {
    Write-Host "Creando entorno virtual en .venv ..."
    & $PyExe -m venv $Venv
}

Write-Host "Instalando paquetes..."
& $VenvPy -m pip install --upgrade pip
& $VenvPy -m pip install -r (Join-Path $Root "requirements.txt")

$Ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $Ffmpeg) {
    Write-Host ""
    Write-Host "AVISO: no hay ffmpeg en el PATH."
    Write-Host "Sin ffmpeg no se pueden abrir muchos videos."
    Write-Host "Instálalo con:  winget install Gyan.FFmpeg"
    Write-Host "Luego cierra y abre la terminal (o reinicia) para que entre en el PATH."
} else {
    Write-Host "ffmpeg OK: $($Ffmpeg.Source)"
}

Write-Host ""
Write-Host "Listo. Abre iniciar.bat o ejecuta crear-acceso.ps1 para el escritorio."
