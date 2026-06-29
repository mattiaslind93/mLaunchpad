#!/bin/bash
#
# HomeLaunchPad launcher for macOS.
#
# Double-click this file in Finder (or run it from Terminal) to start the app.
# On first run it creates a local virtual environment (.venv) and installs the
# dependencies from requirements.txt. Subsequent runs reuse that environment.

# Always operate from the directory this script lives in.
cd "$(dirname "$0")" || exit 1

# Pick the best available Python to build the venv with (prefer Homebrew).
PYTHON_BIN="python3"
for cand in \
    /opt/homebrew/bin/python3.13 \
    /opt/homebrew/bin/python3.12 \
    /opt/homebrew/bin/python3.11 \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    python3; do
    if command -v "$cand" >/dev/null 2>&1; then
        PYTHON_BIN="$cand"
        break
    fi
done

if [ ! -d ".venv" ]; then
    echo "Första körningen – skapar virtuell miljö med $PYTHON_BIN ..."
    "$PYTHON_BIN" -m venv .venv || { echo "Kunde inte skapa venv"; exit 1; }
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt || { echo "Kunde inte installera beroenden"; exit 1; }
fi

exec .venv/bin/python main.py
