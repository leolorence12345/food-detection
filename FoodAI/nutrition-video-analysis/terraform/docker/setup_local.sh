#!/bin/bash
# Setup script to run worker.py locally without Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Setting up local environment for worker.py"
echo "=========================================="
echo ""

# Check Python version
if ! python3 --version | grep -q "3.9\|3.10\|3.11"; then
    echo "⚠️  Warning: Python 3.9-3.11 recommended"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install NumPy first (required before PyTorch)
echo "📦 Installing NumPy 1.24.3..."
pip install "numpy==1.24.3"

# Install PyTorch CPU version
echo "📦 Installing PyTorch (CPU version)..."
pip install torch==2.1.0 torchvision==0.16.0

# Install other dependencies
echo "📦 Installing other dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "To run the test:"
echo "  source venv/bin/activate"
echo "  python3 test_worker_simple.py /path/to/image.png"
echo ""


