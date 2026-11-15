@echo off
setlocal enabledelayedexpansion
title Kerala Tourism Intelligence Platform

echo =====================================================================
echo       KERALA TOURISM INTELLIGENCE PLATFORM - 1-CLICK LAUNCHER
echo =====================================================================
echo.

cd /d "%~dp0"

:: -------------------------------------------------------------------------
:: 1. Detect Python executable
:: -------------------------------------------------------------------------
set "PYTHON_CMD="

:: Check Anaconda dedicated kerala_tourism environment first if available
if exist "%USERPROFILE%\anaconda3\envs\kerala_tourism\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\anaconda3\envs\kerala_tourism\python.exe"
    goto :PYTHON_FOUND
)

:: Try standard python command
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

:: Try Windows Python launcher
py --version >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_CMD=py"
    goto :PYTHON_FOUND
)

:: Check Anaconda base in user profile
if exist "%USERPROFILE%\anaconda3\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\anaconda3\python.exe"
    goto :PYTHON_FOUND
)

:: Check Miniconda in user profile
if exist "%USERPROFILE%\miniconda3\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\miniconda3\python.exe"
    goto :PYTHON_FOUND
)

:: Check AppData Local Programs
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :PYTHON_FOUND
    )
)

:PYTHON_NOT_FOUND
echo [ERROR] Python is not installed or not in your system PATH!
echo.
echo To run this application:
echo  1. Download Python from: https://www.python.org/downloads/
echo  2. During installation, CHECK the box: "Add Python to PATH"
echo  3. After installation completes, double-click run.bat again.
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [*] Using Python: !PYTHON_CMD!

:: -------------------------------------------------------------------------
:: 2. Check if current Python already has all dependencies installed
:: -------------------------------------------------------------------------
"!PYTHON_CMD!" -c "import flask, pandas, plotly, sklearn" >nul 2>&1
if !errorlevel! equ 0 (
    echo [*] Environment dependencies verified successfully.
    set "APP_RUNNER=!PYTHON_CMD!"
    goto :START_APP
)

:: -------------------------------------------------------------------------
:: 3. Verify or setup Virtual Environment (.venv) for isolated install
:: -------------------------------------------------------------------------
set "RECREATE_VENV=0"

if exist ".venv" (
    :: Check if the existing .venv actually works
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [!] Existing .venv is invalid or from another PC.
        echo [*] Rebuilding fresh virtual environment...
        set "RECREATE_VENV=1"
        rmdir /s /q ".venv" >nul 2>&1
    )
)

if not exist ".venv" (
    echo [*] Creating fresh virtual environment (.venv)...
    "!PYTHON_CMD!" -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [*] Virtual environment created successfully.
    set "NEEDS_INSTALL=1"
) else (
    set "NEEDS_INSTALL=0"
)

:: -------------------------------------------------------------------------
:: 4. Check / Install dependencies inside .venv
:: -------------------------------------------------------------------------
".venv\Scripts\python.exe" -c "import flask, pandas, plotly, sklearn" >nul 2>&1
if !errorlevel! neq 0 (
    set "NEEDS_INSTALL=1"
)

if "!NEEDS_INSTALL!"=="1" (
    echo [*] Installing required packages from requirements.txt...
    echo     (This may take 1-2 minutes on first run, please wait...)
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Package installation failed. Please check your internet connection.
        pause
        exit /b 1
    )
    echo [*] All dependencies installed successfully.
)

set "APP_RUNNER=.venv\Scripts\python.exe"

:: -------------------------------------------------------------------------
:: 5. Start the Application
:: -------------------------------------------------------------------------
:START_APP
echo.
echo =====================================================================
echo  Starting server at http://127.0.0.1:5000 ...
echo  Your browser will open automatically. Keep this window open!
echo  Press Ctrl+C to stop the server when done.
echo =====================================================================
echo.

"!APP_RUNNER!" app.py

if !errorlevel! neq 0 (
    echo.
    echo [!] Server stopped or encountered an error.
    pause
)
