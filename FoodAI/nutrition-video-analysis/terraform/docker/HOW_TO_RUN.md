# How to Run the Pipeline - Simple Guide

## Current Status

✅ **Docker image exists** (`nutrition-worker-test:latest`)  
✅ **Docker is running**  
✅ **PyTorch is installed in Docker**  
❌ **Local venv has only 1/22 packages installed**

## Quick Solution: Use Docker (Easiest)

Since Docker already has everything installed, use it:

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Test with an image
bash run_test_docker.sh /path/to/your/image.jpg
```

**If you don't have a test image:**
```bash
# Use any image you have
bash run_test_docker.sh ~/Downloads/food.jpg
```

## Alternative: Finish Local Installation

If you want to run locally (without Docker):

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Activate venv
source venv/bin/activate

# Install all packages (takes 10-15 min, run in YOUR terminal, not Cursor)
pip install -r requirements.txt

# Then run
python3 test_worker_simple.py /path/to/image.jpg
```

## Why Docker "Failed"

Docker didn't actually fail - it's working! The issue is likely:

1. **Missing test image** - `run_test_docker.sh` needs an image file
2. **Missing SAM2 checkpoints** - The script tries to download them automatically
3. **Path issues** - Make sure you're running from the right directory

## Check What's Wrong

Run this to see what's missing:

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Check if Docker image exists
docker images | grep nutrition-worker-test

# Check if checkpoints exist
ls -lh checkpoints/sam2.1_hiera_base_plus.pt

# Test Docker works
docker run --rm nutrition-worker-test:latest python3 --version
```

## Common Issues

### Issue 1: "Test image not found"
**Fix:** Provide a path to an image file
```bash
bash run_test_docker.sh /absolute/path/to/image.jpg
```

### Issue 2: "Checkpoint file not found"
**Fix:** The script will download it automatically, or download manually:
```bash
cd checkpoints
curl -L -O https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt
```

### Issue 3: "Docker build failed"
**Fix:** Rebuild the image (takes 15-20 min):
```bash
docker build -t nutrition-worker-test -f Dockerfile .
```

## Summary

**Easiest path:** Use Docker (already built!)
```bash
bash run_test_docker.sh /path/to/image.jpg
```

**If Docker fails:** Check the error message and fix the specific issue (usually missing files or paths)


