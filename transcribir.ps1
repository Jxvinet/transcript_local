param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Archivo,
    [string]$Modelo = "",
    [string]$Formatos = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Script = Join-Path $Root "transcribir.py"

if (-not (Test-Path $Python)) {
    throw "Falta .venv. Ejecuta instalar.ps1 primero."
}
if (-not (Test-Path -LiteralPath $Archivo)) {
    throw "No existe el archivo: $Archivo"
}

$argsList = @($Script, $Archivo)
if ($Modelo) { $argsList += @("--modelo", $Modelo) }
if ($Formatos) { $argsList += @("--formatos", $Formatos) }

& $Python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
