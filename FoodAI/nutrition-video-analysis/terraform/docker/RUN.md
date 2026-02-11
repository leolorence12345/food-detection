# How to Run the Nutrition Pipeline

## 🚀 Quick Start

### Option 1: Using Docker (Easiest - Everything Pre-installed)

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Run on your image
docker run --rm \
  -v "$(pwd):/app" \
  -v "$(pwd)/checkpoints:/app/checkpoints" \
  -e DEVICE=cpu \
  nutrition-worker-test:latest \
  python3 run_pipeline.py /app/../../image.png
```

Or use the wrapper script:
```bash
bash run_test_docker.sh /Users/leo/FoodProject/food-detection/image.png
```

### Option 2: Run Locally (Direct Python)

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Activate virtual environment
source venv/bin/activate

# Run pipeline
python3 run_pipeline.py /Users/leo/FoodProject/food-detection/image.png
```

**Note:** Make sure dependencies are installed first (see below).

### Option 3: Run API Server

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Using Docker
docker run --rm -p 8000:8000 \
  -v "$(pwd):/app" \
  nutrition-worker-test:latest \
  python3 -m app.api

# Or locally
source venv/bin/activate
python3 -m app.api
```

Then upload images via:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/image.jpg"
```

## 📋 Prerequisites

### For Docker:
- Docker Desktop running
- Docker image built: `nutrition-worker-test`

### For Local:
- Python 3.9-3.11
- Virtual environment with dependencies installed
- Models downloaded (SAM2 checkpoint, etc.)

## 🔧 Install Dependencies (Local Only)

If running locally and dependencies aren't installed:

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Create venv if needed
python3 -m venv venv

# Activate
source venv/bin/activate

# Install (takes 10-15 minutes)
pip install -r requirements.txt
```

## 📊 Output

After running, you'll get:

1. **Console output** with detected foods and calories
2. **JSON file** (`results.json`) with full results
3. **Output images** in `data/outputs/` directory

Example output:
```
Detected 3 food items:

  1. burger
     Calories: 300 kcal
     Volume: 150 ml

  2. fries
     Calories: 250 kcal
     Volume: 100 ml

Meal Summary:
  Total Calories: 550 kcal
  Total Volume: 250 ml
  Food Items: 2
```

## 🎯 What Happens

1. **Loads image** → Resizes to 800px width
2. **Detects objects** → Florence-2 finds food items
3. **Tracks objects** → SAM2 creates precise masks
4. **Estimates depth** → Metric3D creates 3D depth map
5. **Calculates volume** → From depth + mask + calibration
6. **Looks up nutrition** → RAG system finds calories
7. **Returns results** → JSON with all info

## 🐛 Troubleshooting

### "Module not found"
- Make sure you're in the `docker/` directory
- Activate venv: `source venv/bin/activate`
- Or use Docker instead

### "Checkpoint not found"
- SAM2 checkpoint should be in `checkpoints/sam2.1_hiera_base_plus.pt`
- Download if missing (script handles this automatically)

### "CUDA out of memory" or "Device errors"
- Set `DEVICE=cpu` environment variable
- Pipeline works on CPU (slower but functional)

### Path errors
- Use absolute paths for images: `/Users/leo/FoodProject/food-detection/image.png`
- Or relative paths from the `docker/` directory

## 📝 Example Commands

```bash
# Process single image
python3 run_pipeline.py /path/to/food.jpg

# Process multiple images
for img in ~/Downloads/*.jpg; do
  python3 run_pipeline.py "$img"
done

# Process video
python3 run_pipeline.py /path/to/video.mp4
```


