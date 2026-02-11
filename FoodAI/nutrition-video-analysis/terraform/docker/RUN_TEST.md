# Running the Worker Test

## Fixed Dockerfile Issue
The Dockerfile has been updated to fix the PyTorch installation issue. The problem was that `torch==2.1.0+cpu` is no longer available from PyTorch's CPU index. The fix uses the regular PyPI version which works fine for CPU.

## Steps to Run the Test

1. **Make sure Docker Desktop is running**
   - Check the menu bar for the Docker icon
   - It should show "Docker Desktop is running"

2. **Run the test script:**
   ```bash
   cd /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker
   bash run_test_docker.sh /Users/leo/FoodProject/food-detection/image.png
   ```

3. **First build will take 10-15 minutes**
   - The Docker image needs to be built the first time
   - It will download and install all dependencies
   - Subsequent runs will be much faster

4. **What the test does:**
   - Processes your burger image through the nutrition analysis pipeline
   - Detects food items (burger, fries, etc.)
   - Calculates nutrition estimates
   - Saves results to `test_results/` directory

## Troubleshooting

If you get permission errors:
```bash
# Make sure Docker Desktop is running
# You may need to restart Docker Desktop or your terminal
```

If the build fails:
- Check your internet connection (needs to download packages)
- Make sure you have enough disk space
- The build downloads several GB of dependencies

## Expected Output

You should see:
- Building Docker image...
- Processing image...
- Detected food items with calories
- Results saved to test_results/


