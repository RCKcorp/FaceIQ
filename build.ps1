$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) { py -3.11 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe -m pytest
& .\.venv\Scripts\pyinstaller.exe --noconfirm --clean FaceIQ.spec
$isccCandidates = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($iscc) {
    & $iscc "installer\FaceIQ.iss"
    Write-Host "Setup termine : dist\installer\FaceIQ-Setup-1.0.0.exe" -ForegroundColor Green
} else {
    Write-Warning "Inno Setup 6 absent : EXE créé, setup non généré."
}
Write-Host ""
Write-Host "Build termine : dist\FaceIQ.exe" -ForegroundColor Green
