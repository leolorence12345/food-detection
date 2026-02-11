# Next Steps - Run Your Pipeline

## 🚀 Quick Start: Run on an Image

You have two options:

### Option 1: Use Docker (Recommended - Everything Already Installed)

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Run on your image
bash RUN_NOW.sh /Users/leo/FoodProject/food-detection/image.png
```

Or use the original script:
```bash
bash run_test_docker.sh /Users/leo/FoodProject/food-detection/image.png
```

### Option 2: Run Locally (If Dependencies Installed)

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Activate venv
source venv/bin/activate

# Run test
python3 test_worker_simple.py /Users/leo/FoodProject/food-detection/image.png
```

## 📊 View Results

After running, check:

1. **JSON Results:**
   ```bash
   cat test_results/test-*/results.json
   ```

2. **Output Images:**
   ```bash
   ls -lh data/outputs/test-*/frames_temp/
   ```

3. **View in Finder:**
   ```bash
   open test_results/
   open data/outputs/
   ```

## 🔍 What the Pipeline Does

1. **Detects food items** using Florence-2
2. **Tracks objects** using SAM2
3. **Estimates depth** using Metric3D
4. **Calculates volumes** from depth maps
5. **Looks up nutrition** from RAG database
6. **Returns calories** and nutrition info

## 📝 Example Output

The results JSON will contain:
```json
{
  "detected_items": [
    {
      "name": "burger",
      "calories": 250,
      "volume_ml": 150
    }
  ],
  "meal_summary": {
    "total_calories": 500,
    "total_volume_ml": 300
  }
}
```

## 🎯 Common Tasks

### Run on Multiple Images
```bash
for img in ~/Downloads/*.jpg; do
  bash RUN_NOW.sh "$img"
done
```

### Check Installation Progress (Local)
```bash
source venv/bin/activate
python3 check_install_progress.py
```

### View Latest Results
```bash
# Find latest test result
ls -t test_results/*.json | head -1 | xargs cat | python3 -m json.tool
```

## 🐛 Troubleshooting

### "Image not found"
- Use absolute path: `/Users/leo/FoodProject/food-detection/image.png`
- Or relative path from docker folder

### "Docker image not found"
```bash
docker build -t nutrition-worker-test -f Dockerfile .
```

### "Checkpoint not found"
The script downloads it automatically, but if it fails:
```bash
cd checkpoints
curl -L -O https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt
```

## ✅ You're Ready!

Just run:
```bash
bash RUN_NOW.sh /path/to/your/image.jpg
```


