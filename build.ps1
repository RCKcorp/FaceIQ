$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) { py -3.11 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe -m pytest
& .\.venv\Scripts\pyinstaller.exe --noconfirm --clean FaceIQ.spec
Write-Host ""
Write-Host "Build termine : dist\FaceIQ.exe" -ForegroundColor Green
Write-Host "Pour creer le setup, compilez installer\FaceIQ.iss avec Inno Setup 6." -ForegroundColor Cyan
