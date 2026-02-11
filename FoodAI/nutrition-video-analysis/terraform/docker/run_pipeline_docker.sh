#!/bin/bash
# Run pipeline in Docker with proper path handling

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -z "$1" ]; then
    echo "Usage: $0 <image_path>"
    echo "Example: $0 /Users/leo/FoodProject/food-detection/image.png"
    exit 1
fi

IMAGE_PATH="$1"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: Image not found: $IMAGE_PATH"
    exit 1
fi

# Get absolute path
IMAGE_PATH=$(cd "$(dirname "$IMAGE_PATH")" && pwd)/$(basename "$IMAGE_PATH")

echo "=========================================="
echo "Running Nutrition Pipeline in Docker"
echo "=========================================="
echo "Image: $IMAGE_PATH"
echo ""

# Copy image to a location Docker can access
TEMP_IMAGE="/tmp/docker_image_$(basename "$IMAGE_PATH")"
cp "$IMAGE_PATH" "$TEMP_IMAGE"

# Run in Docker
docker run --rm \
  -v "$SCRIPT_DIR:/app" \
  -v "$SCRIPT_DIR/checkpoints:/app/checkpoints" \
  -v "/tmp:/tmp" \
  -e DEVICE=cpu \
  nutrition-worker-test:latest \
  python3 run_pipeline.py "/tmp/$(basename "$TEMP_IMAGE")"

# Cleanup
rm -f "$TEMP_IMAGE"

echo ""
echo "✅ Done! Check results.json in the docker directory"


