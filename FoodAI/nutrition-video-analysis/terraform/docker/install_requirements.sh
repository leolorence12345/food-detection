#!/bin/bash
# Install requirements for local pipeline execution
# This script handles the installation step by step to avoid timeouts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Installing Pipeline Requirements"
echo "=========================================="
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup_local.sh first."
    exit 1
fi

source venv/bin/activate

echo "📦 Step 1/4: Installing NumPy (already done if you see this)..."
pip install "numpy==1.24.3" --quiet

echo "📦 Step 2/4: Installing PyTorch (this is LARGE ~500MB, will take 5-10 minutes)..."
echo "   ⏳ Please be patient - downloading PyTorch..."
pip install torch==2.1.0 torchvision==0.16.0

echo "📦 Step 3/4: Installing core dependencies..."
pip install \
    transformers>=4.40.0,<4.45.0 \
    opencv-python-headless==4.8.1.78 \
    Pillow==10.1.0 \
    scipy==1.11.4 \
    einops==0.7.0

echo "📦 Step 4/4: Installing remaining dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "To test the pipeline:"
echo "  source venv/bin/activate"
echo "  python3 test_worker_simple.py /path/to/your/image.jpg"
echo ""


