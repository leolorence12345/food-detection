#!/bin/bash
# Simple script to run the pipeline RIGHT NOW

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "🚀 Running Nutrition Pipeline"
echo "=========================================="
echo ""

# Check if test image provided
if [ -z "$1" ]; then
    echo "❌ Error: No image provided"
    echo ""
    echo "Usage:"
    echo "  bash RUN_NOW.sh /path/to/your/image.jpg"
    echo ""
    echo "Example:"
    echo "  bash RUN_NOW.sh ~/Downloads/food.jpg"
    exit 1
fi

IMAGE_PATH="$1"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Error: Image not found: $IMAGE_PATH"
    exit 1
fi

echo "📸 Image: $IMAGE_PATH"
echo ""

# Check Docker
if ! docker images | grep -q "nutrition-worker-test"; then
    echo "❌ Docker image not found. Building it now..."
    echo "   (This takes 15-20 minutes, but only needs to be done once)"
    docker build -t nutrition-worker-test -f Dockerfile .
fi

echo "✅ Docker image ready"
echo ""

# Run the test
echo "🚀 Processing image..."
echo ""

bash run_test_docker.sh "$IMAGE_PATH"

echo ""
echo "=========================================="
echo "✅ Done! Check test_results/ for output"
echo "=========================================="


