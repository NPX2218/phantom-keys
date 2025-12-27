#!/bin/bash
# Phantom Keys Setup Script
# Usage: source setup.sh

echo "Phantom Keys - Setup"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "  macOS:  brew install python3"
    echo "  Ubuntu: sudo apt install python3 python3-venv python3-pip"
    return 1 2>/dev/null || exit 1
fi

echo "Found: $(python3 --version)"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        return 1 2>/dev/null || exit 1
    fi
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install pyautogui --quiet

echo ""
echo "Setup complete. Run: python main.py"