#!/bin/bash
# Simple Docker test - shows what's failing

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "Testing Docker Setup"
echo "=========================================="
echo ""

# Check if image exists
if ! docker images | grep -q "nutrition-worker-test"; then
    echo "❌ Docker image 'nutrition-worker-test' not found"
    echo ""
    echo "Build it with:"
    echo "  docker build -t nutrition-worker-test -f Dockerfile ."
    exit 1
fi

echo "✅ Docker image found"
echo ""

# Test 1: Python works
echo "Test 1: Python version..."
docker run --rm nutrition-worker-test:latest python3 --version
echo "✅ Python works"
echo ""

# Test 2: PyTorch works
echo "Test 2: PyTorch import..."
docker run --rm nutrition-worker-test:latest python3 -c "import torch; print('✅ PyTorch:', torch.__version__)"
echo ""

# Test 3: Check if worker.py exists
echo "Test 3: Worker script..."
docker run --rm nutrition-worker-test:latest ls -la /app/worker.py
echo "✅ Worker script exists"
echo ""

# Test 4: Check imports
echo "Test 4: Importing modules..."
docker run --rm nutrition-worker-test:latest python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from app.pipeline import NutritionVideoPipeline
    print('✅ Pipeline imports OK')
except Exception as e:
    print(f'❌ Pipeline import failed: {e}')
    sys.exit(1)
"
echo ""

echo "=========================================="
echo "✅ All Docker tests passed!"
echo "=========================================="
echo ""
echo "To run the actual pipeline:"
echo "  bash run_test_docker.sh /path/to/image.jpg"
echo ""


