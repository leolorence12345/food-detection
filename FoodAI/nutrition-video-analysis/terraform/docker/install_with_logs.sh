#!/bin/bash
# Install with visible progress logs

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "Installing Dependencies with Full Logs"
echo "=========================================="
echo ""

# Activate venv
if [ ! -d "venv" ]; then
    echo "❌ venv not found. Run: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

echo "📦 Installing packages (you'll see all logs)..."
echo ""

# Install with verbose output and progress bar
pip install --verbose --progress-bar on -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "Check progress: python3 check_install_progress.py"


