# build_pdf.ps1
# -----------------------------------------------------------------------------
# Genera ventas/propuesta.pdf a partir de ventas/index.html usando el
# impresor headless de Chrome o Edge. No requiere dependencias externas.
#
# Uso:
#   powershell -ExecutionPolicy Bypass -File ventas\build_pdf.ps1
# -----------------------------------------------------------------------------

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$htmlPath = Join-Path $scriptDir "index.html"
$pdfPath = Join-Path $scriptDir "propuesta.pdf"

if (-not (Test-Path -LiteralPath $htmlPath)) {
    throw "No se encontro el archivo: $htmlPath"
}

$candidates = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

$browser = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $browser) {
    throw "No se encontro Chrome ni Edge. Instalá uno de los dos para generar el PDF."
}

$fileUrl = "file:///" + ($htmlPath -replace '\\', '/')

Write-Host "Usando navegador: $browser"
Write-Host "Fuente: $htmlPath"
Write-Host "Salida:  $pdfPath"

if (Test-Path -LiteralPath $pdfPath) {
    Remove-Item -LiteralPath $pdfPath -Force
}

& $browser `
    --headless=new `
    --disable-gpu `
    --no-pdf-header-footer `
    --virtual-time-budget=10000 `
    --print-to-pdf="$pdfPath" `
    "$fileUrl"

# Chrome/Edge pueden retornar antes de terminar de escribir el archivo.
$timeout = 30
$elapsed = 0
while (-not (Test-Path -LiteralPath $pdfPath) -and $elapsed -lt $timeout) {
    Start-Sleep -Milliseconds 500
    $elapsed += 0.5
}

if (-not (Test-Path -LiteralPath $pdfPath)) {
    throw "El navegador no genero el PDF. Revisa que Chrome/Edge pueda ejecutarse en headless."
}

Write-Host "PDF generado correctamente: $pdfPath"
