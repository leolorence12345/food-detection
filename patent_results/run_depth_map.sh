#!/bin/bash
# Activate virtual environment and run depth map generation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="/Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker/venv"

cd "$SCRIPT_DIR"

if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    echo "✓ Virtual environment activated"
else
    echo "Warning: Virtual environment not found at $VENV_PATH"
    echo "Continuing without activation..."
fi

echo "Running depth map generation..."
export MPLCONFIGDIR="$SCRIPT_DIR"
export DEVICE="${DEVICE:-cpu}"

python3 generate_depth_map.py
