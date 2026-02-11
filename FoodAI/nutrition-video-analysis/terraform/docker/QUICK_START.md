# Quick Start - Run Pipeline Locally

## Option 1: Install Dependencies (Recommended)

**Run this in your terminal** (not through Cursor - it times out):

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Activate venv
source venv/bin/activate

# Install with visible logs
pip install --verbose --progress-bar on -r requirements.txt
```

This will show you:
- ✅ Which packages are downloading
- ✅ Download progress bars
- ✅ Installation status
- ✅ Any errors immediately

**Time:** 10-15 minutes (PyTorch is ~500MB)

## Option 2: Use Docker (Easier, but needs Docker running)

```bash
cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Build Docker image (one time, takes 15-20 min)
docker build -t nutrition-worker .

# Run test
bash run_test_docker.sh /path/to/your/image.jpg
```

## Check Progress

While installing, check progress:
```bash
source venv/bin/activate
python3 check_install_progress.py
```

## Run Pipeline After Installation

```bash
source venv/bin/activate
python3 test_worker_simple.py /path/to/your/image.jpg
```

## Why Cursor Times Out?

- PyTorch is 500MB+ download
- Network timeouts in sandboxed environment
- **Solution:** Run `pip install` directly in your terminal


