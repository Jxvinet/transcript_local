# Crea/actualiza el acceso directo "Transcribir reunion" en el escritorio.

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
$Lnk = Join-Path $Desktop "Transcribir reunion.lnk"
$W = New-Object -ComObject WScript.Shell
$S = $W.CreateShortcut($Lnk)
$S.TargetPath = $VenvPyw
$S.Arguments = '"' + $Gui + '"'
$S.WorkingDirectory = $Root
$Ico = Join-Path $Root "icono-j.ico"
$S.Description = "Transcribir video o audio a Word"
if (Test-Path $Ico) {
    $S.IconLocation = "$Ico,0"
} else {
    $S.IconLocation = "imageres.dll,15"
}
$S.Save()

Write-Host "Listo: $Lnk"
