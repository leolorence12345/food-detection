"""
Quick fix script: Removes/renames the Git LFS pointer directory and loads the dataset.

Run this if you're having issues with Git LFS pointer files.
"""

import shutil
from pathlib import Path
from datasets import load_dataset

# Path to the problematic directory
food101_dir = Path(__file__).parent / "food101"
backup_dir = Path(__file__).parent / "food101_backup_lfs_pointers"

print("=" * 60)
print("Food-101 Dataset Loader (Git LFS Fix)")
print("=" * 60)

# Check if food101 directory exists and has LFS pointers
if food101_dir.exists():
    parquet_file = food101_dir / "data" / "train-00000-of-00008.parquet"
    if parquet_file.exists():
        try:
            content = parquet_file.read_text()
            if "version https://git-lfs" in content:
                print("\n⚠ Found Git LFS pointer files in food101/ directory")
                print("   These are not actual data files.")
                
                # Ask user what to do (or just rename automatically)
                print(f"\nRenaming {food101_dir} to {backup_dir}...")
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                food101_dir.rename(backup_dir)
                print("✓ Directory renamed successfully")
            else:
                print("\n✓ food101/ directory contains actual data files")
        except Exception as e:
            print(f"⚠ Could not check files: {e}")
    else:
        print("\n✓ food101/ directory exists but no parquet files found")
else:
    print("\n✓ No local food101/ directory found - will download fresh")

# Now load the dataset
print("\n" + "=" * 60)
print("Loading Food-101 dataset from Hugging Face...")
print("=" * 60)
print("This may take a few minutes on first run (~5GB download)")
print()

try:
    dataset = load_dataset("food101", split="train")
    print(f"\n✓ Successfully loaded {len(dataset)} training images")
    
    # Test access
    print("\nTesting image access...")
    image = dataset[0]['image']
    label = dataset[0]['label']
    label_names = dataset.features['label'].names
    label_name = label_names[label]
    
    print(f"  First image: {label_name} (ID: {label})")
    print(f"  Image size: {image.size}")
    print(f"  Image mode: {image.mode}")
    
    print("\n" + "=" * 60)
    print("✓ Dataset loaded successfully!")
    print("=" * 60)
    print("\nYou can now use:")
    print("  from access_images import load_dataset_from_cache")
    print("  dataset = load_dataset_from_cache(split='train')")
    
except Exception as e:
    print(f"\n❌ Error loading dataset: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you have internet connection")
    print("2. Check that datasets library is installed: pip install datasets")
    print("3. Try deleting the food101 directory: rm -rf food101")
    raise
