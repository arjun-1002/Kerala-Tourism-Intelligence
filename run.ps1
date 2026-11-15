# Kerala Tourism Intelligence Platform - PowerShell Launcher
$ErrorActionPreference = "Stop"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "      KERALA TOURISM INTELLIGENCE PLATFORM - LAUNCHER" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# 1. Detect Python
$pythonCmd = $null
if (Test-Path "$env:USERPROFILE\anaconda3\envs\kerala_tourism\python.exe") {
    $pythonCmd = "$env:USERPROFILE\anaconda3\envs\kerala_tourism\python.exe"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Test-Path "$env:USERPROFILE\anaconda3\python.exe") {
    $pythonCmd = "$env:USERPROFILE\anaconda3\python.exe"
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Download Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Ensure you check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

Write-Host "[*] Found Python: $pythonCmd" -ForegroundColor Green

# 2. Check / Setup Virtual Environment
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$needsInstall = $false

if (Test-Path ".venv") {
    try {
        & $venvPython -c "import sys" 2>$null
        if ($LASTEXITCODE -ne 0) { throw "Corrupt venv" }
    } catch {
        Write-Host "[!] Existing .venv is invalid. Rebuilding fresh environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force ".venv"
    }
}

if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating fresh virtual environment (.venv)..." -ForegroundColor Cyan
    & $pythonCmd -m venv .venv
    $needsInstall = $true
}

# 3. Check dependencies
try {
    & $venvPython -c "import flask, pandas, plotly, sklearn" 2>$null
    if ($LASTEXITCODE -ne 0) { $needsInstall = $true }
} catch {
    $needsInstall = $true
}

if ($needsInstall) {
    Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
    Write-Host "[*] Dependencies installed successfully." -ForegroundColor Green
}

# 4. Start Application
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host " Starting server at http://127.0.0.1:5000 ..." -ForegroundColor Green
Write-Host " Opening browser automatically..." -ForegroundColor Green
Write-Host " Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

& $venvPython app.py
