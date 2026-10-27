# Crea/actualiza el acceso directo "transcript_local" en el escritorio.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPyw = Join-Path $Root ".venv\Scripts\pythonw.exe"
$Gui = Join-Path $Root "gui.py"

if (-not (Test-Path $VenvPyw)) {
    throw "Falta .venv. Ejecuta antes instalar.ps1"
}
if (-not (Test-Path $Gui)) {
    throw "Falta gui.py en $Root"
}

$Desktop = [Environment]::GetFolderPath("Desktop")
$Lnk = Join-Path $Desktop "transcript_local.lnk"
$OldNames = @(
    "Transcribir reunion.lnk",
    "Transcripciones en local.lnk"
)
$W = New-Object -ComObject WScript.Shell
$S = $W.CreateShortcut($Lnk)
$S.TargetPath = $VenvPyw
$S.Arguments = '"' + $Gui + '"'
$S.WorkingDirectory = $Root
$Ico = Join-Path $Root "icono-j.ico"
$S.Description = "transcript_local: video o audio a Word en tu PC"
if (Test-Path $Ico) {
    $S.IconLocation = "$Ico,0"
} else {
    $S.IconLocation = "imageres.dll,15"
}
$S.Save()
foreach ($name in $OldNames) {
    $old = Join-Path $Desktop $name
    if ((Test-Path -LiteralPath $old) -and ($old -ne $Lnk)) {
        Remove-Item -LiteralPath $old -Force
    }
}

Write-Host "Listo: $Lnk"
