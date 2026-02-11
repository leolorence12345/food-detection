"""
Script to show where the Food-101 dataset is cached.
"""

import os
from pathlib import Path

# Get Hugging Face cache location
XDG_CACHE_HOME = os.getenv("XDG_CACHE_HOME", "~/.cache")
HF_CACHE_HOME = os.path.expanduser(os.getenv("HF_HOME", os.path.join(XDG_CACHE_HOME, "huggingface")))
HF_DATASETS_CACHE = Path(os.getenv("HF_DATASETS_CACHE", os.path.join(HF_CACHE_HOME, "datasets")))

print("=" * 60)
print("Hugging Face Datasets Cache Location")
print("=" * 60)
print(f"\nDefault cache directory: {HF_DATASETS_CACHE}")
print(f"Absolute path: {HF_DATASETS_CACHE.resolve()}")

# Check if it exists
if HF_DATASETS_CACHE.exists():
    print(f"\n✓ Cache directory exists")
    
    # Look for food101 dataset
    food101_dirs = list(HF_DATASETS_CACHE.glob("*food101*"))
    if food101_dirs:
        print(f"\nFound Food-101 dataset directories:")
        for dir_path in food101_dirs:
            print(f"  - {dir_path}")
            if dir_path.is_dir():
                # Check size
                total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                size_gb = total_size / (1024**3)
                print(f"    Size: {size_gb:.2f} GB")
    else:
        print(f"\n⚠ No food101 directories found in cache")
        print(f"   (Dataset might be stored elsewhere or not yet cached)")
else:
    print(f"\n⚠ Cache directory does not exist yet")
    print(f"   (Will be created when you first load a dataset)")

# Also check the local gemini directory
print("\n" + "=" * 60)
print("Local Project Directory")
print("=" * 60)
local_food101 = Path(__file__).parent / "food101"
if local_food101.exists():
    print(f"\nLocal food101 directory: {local_food101}")
    print(f"  ⚠ Note: This contains Git LFS pointers, not actual data")
else:
    print(f"\nNo local food101 directory found")

# Try to get actual cache location from a loaded dataset
print("\n" + "=" * 60)
print("Actual Dataset Cache Location")
print("=" * 60)
try:
    from datasets import load_dataset
    print("\nLoading dataset to find cache location...")
    dataset = load_dataset("food101", split="train")
    
    if hasattr(dataset, 'cache_files') and dataset.cache_files:
        cache_file = dataset.cache_files[0]['filename']
        cache_dir = Path(cache_file).parent
        print(f"\n✓ Actual cache location: {cache_dir}")
        print(f"  Cache file example: {cache_file}")
        
        # Get parent directories
        print(f"\nCache directory structure:")
        current = cache_dir
        depth = 0
        while current != HF_DATASETS_CACHE and depth < 10:
            print(f"  {'  ' * depth}└── {current.name}")
            current = current.parent
            depth += 1
    else:
        print("\n⚠ Could not determine cache file location")
        
except Exception as e:
    print(f"\n⚠ Could not load dataset: {e}")
    print("   Make sure you're in the virtual environment with datasets installed")

print("\n" + "=" * 60)
