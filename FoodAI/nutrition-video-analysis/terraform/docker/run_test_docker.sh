#!/bin/bash
# Docker-based test script for worker.py
# This script runs the worker test inside a Docker container with all dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"

# Default test image
TEST_IMAGE="${1:-$PROJECT_ROOT/image.png}"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "❌ Error: Test image not found: $TEST_IMAGE"
    echo ""
    echo "Usage: $0 [path_to_image]"
    exit 1
fi

echo "=========================================="
echo "🧪 Testing worker.py with Docker"
echo "=========================================="
echo ""
echo "Test image: $TEST_IMAGE"
echo ""

# Check if Docker image exists, if not build it
IMAGE_NAME="nutrition-worker-test"
if ! docker images | grep -q "$IMAGE_NAME"; then
    echo "📦 Building Docker image (this may take a while)..."
    cd "$SCRIPT_DIR"
    docker build -t "$IMAGE_NAME" -f Dockerfile .
    echo "✅ Docker image built"
    echo ""
fi

# Create test results directory
RESULTS_DIR="$SCRIPT_DIR/test_results"
mkdir -p "$RESULTS_DIR"

# Copy test image to a temp location that Docker can access
TEMP_IMAGE="/tmp/test_image_$(basename "$TEST_IMAGE")"
cp "$TEST_IMAGE" "$TEMP_IMAGE"

# Ensure sam2 directory exists in local directory (needed when mounting /app)
# The Docker image has sam2 built-in, but mounting overwrites it
if [ ! -d "$SCRIPT_DIR/sam2" ]; then
    echo "📦 Copying sam2 directory for local mount..."
    cp -r "$SCRIPT_DIR/sam2_package/sam2" "$SCRIPT_DIR/sam2"
fi

# Ensure checkpoints directory exists (needed when mounting /app)
if [ ! -d "$SCRIPT_DIR/checkpoints" ]; then
    echo "📦 Setting up checkpoints directory..."
    mkdir -p "$SCRIPT_DIR/checkpoints"
    
    # Check if checkpoint file exists
    if [ ! -f "$SCRIPT_DIR/checkpoints/sam2.1_hiera_base_plus.pt" ]; then
        echo "⚠️  Checkpoint file not found. Downloading..."
        echo "   This may take a few minutes (file is ~1.5GB)..."
        cd "$SCRIPT_DIR/checkpoints"
        if [ -f "$SCRIPT_DIR/sam2_package/checkpoints/download_ckpts.sh" ]; then
            # Download only the base_plus checkpoint we need
            curl -L -O "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt" || {
                echo "❌ Failed to download checkpoint. You may need to download it manually."
                echo "   URL: https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt"
                exit 1
            }
        else
            echo "❌ Download script not found. Please download checkpoints manually."
            exit 1
        fi
        cd "$SCRIPT_DIR"
    fi
fi

echo "🚀 Running worker test in Docker container..."
echo ""

# Run the test script inside Docker
# Note: We mount /app to allow test script access, but this overwrites the built-in /app
# So we need sam2 to exist in the local directory (copied above)
docker run --rm \
    -v "$SCRIPT_DIR:/app" \
    -v "$RESULTS_DIR:/app/test_results" \
    -v "$(dirname "$TEMP_IMAGE"):/test_images" \
    -e DEVICE=cpu \
    -e S3_VIDEOS_BUCKET=mock-bucket \
    -e S3_RESULTS_BUCKET=mock-results-bucket \
    -e S3_MODELS_BUCKET=mock-models-bucket \
    -e DYNAMODB_JOBS_TABLE=mock-jobs-table \
    -e SQS_VIDEO_QUEUE_URL=mock-queue-url \
    -e GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
    "$IMAGE_NAME" \
    python3 /app/test_worker_local.py "/test_images/$(basename "$TEMP_IMAGE")"

# Cleanup
rm -f "$TEMP_IMAGE"

echo ""
echo "=========================================="
echo "✅ Test completed!"
echo "=========================================="
echo ""
echo "Results saved to: $RESULTS_DIR"

