#!/bin/bash
# Install dependencies locally

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "Installing Dependencies Locally"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install NumPy first (critical for PyTorch)
echo "📦 Installing NumPy 1.24.3..."
pip install "numpy==1.24.3" --quiet

# Install PyTorch CPU
echo "📦 Installing PyTorch (CPU version)..."
echo "   This is large (~500MB), will take a few minutes..."
pip install torch==2.1.0 torchvision==0.16.0

# Install other dependencies
echo "📦 Installing other dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "To run the pipeline:"
echo "  source venv/bin/activate"
echo "  python3 run_pipeline.py /path/to/image.png"
echo ""


