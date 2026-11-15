#!/usr/bin/env bash
# Kerala Tourism Intelligence Platform - 1-Click Launcher (macOS / Linux)

set -e

echo "====================================================================="
echo "      KERALA TOURISM INTELLIGENCE PLATFORM - 1-CLICK LAUNCHER"
echo "====================================================================="
echo ""

cd "$(dirname "$0")"

# 1. Detect Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not in your PATH."
    echo "Please install Python 3 (https://www.python.org/downloads/) and try again."
    exit 1
fi

echo "[*] Using Python: $($PYTHON_CMD --version)"

# 2. Check / Setup Virtual Environment
if [ -d ".venv" ]; then
    # Test if .venv is working
    if ! .venv/bin/python -c "import sys" &>/dev/null; then
        echo "[!] Existing .venv is broken (e.g. from another OS or machine). Recreating..."
        rm -rf .venv
    fi
fi

if [ ! -d ".venv" ]; then
    echo "[*] Creating fresh virtual environment (.venv)..."
    $PYTHON_CMD -m venv .venv
    NEEDS_INSTALL=1
else
    NEEDS_INSTALL=0
fi

# 3. Check / Install dependencies
if ! .venv/bin/python -c "import flask, pandas, plotly, sklearn" &>/dev/null; then
    NEEDS_INSTALL=1
fi

if [ "$NEEDS_INSTALL" -eq 1 ]; then
    echo "[*] Installing required packages from requirements.txt..."
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
    echo "[*] All dependencies installed successfully."
fi

# 4. Start Application
echo ""
echo "====================================================================="
echo "  Starting server at http://127.0.0.1:5000 ..."
echo "  Press Ctrl+C to stop the server."
echo "====================================================================="
echo ""

.venv/bin/python app.py
