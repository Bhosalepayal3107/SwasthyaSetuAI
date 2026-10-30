# HealthSahayAI PowerShell Launcher
Set-Location -Path $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting HealthSahayAI (SwasthyaSetu AI)" -ForegroundColor Green
Write-Host "  Local Portal: http://127.0.0.1:5000/" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "Running with .venv (Python 3.12)..." -ForegroundColor Gray
    & ".\.venv\Scripts\python.exe" app.py
} elseif (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe") {
    Write-Host "Running with installed Python 3.12..." -ForegroundColor Gray
    & "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" app.py
} else {
    Write-Host "Running with default python..." -ForegroundColor Gray
    python app.py
}

