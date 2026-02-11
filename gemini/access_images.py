"""
Simple script to access images from the Food-101 dataset.

The dataset will be downloaded from Hugging Face if not already cached.
This script provides easy access to the images and labels.
"""

from datasets import load_dataset
from PIL import Image
import os
import shutil
from pathlib import Path


def load_dataset_from_cache(split="train", cache_dir=None):
    """
    Load the Food-101 dataset from Hugging Face.
    
    This function will download the dataset if it's not already cached,
    or use the cached version if available. If Git LFS pointers are detected
    in the local food101 directory, it will temporarily rename that directory
    to force Hugging Face to download the actual files.
    
    Args:
        split: Dataset split to load. Options: "train" or "validation"
        cache_dir: Optional cache directory. If None, uses default Hugging Face cache.
    
    Returns:
        Dataset: Hugging Face dataset object
    """
    import tempfile
    import shutil
    
    # Check if local food101 directory has Git LFS pointers
    local_food101_dir = Path(__file__).parent / "food101"
    backup_dir = None
    has_lfs_pointers = False
    
    if local_food101_dir.exists():
        parquet_file = local_food101_dir / "data" / "train-00000-of-00008.parquet"
        if parquet_file.exists():
            try:
                content = parquet_file.read_text()
                if "version https://git-lfs" in content or "git-lfs" in content.lower():
                    has_lfs_pointers = True
                    print("⚠ Detected Git LFS pointer files in local food101/ directory.")
                    print("   Temporarily renaming it to force Hugging Face to download actual files...")
                    print("   This may take a few minutes on first run (~5GB download).")
                    
                    # Temporarily rename the directory so Hugging Face doesn't find it
                    backup_dir = local_food101_dir.parent / "food101_backup_lfs_pointers"
                    if backup_dir.exists():
                        shutil.rmtree(backup_dir)
                    local_food101_dir.rename(backup_dir)
                    print(f"   Renamed {local_food101_dir} to {backup_dir}")
            except Exception as e:
                print(f"   Warning: Could not check/rename food101 directory: {e}")
    
    # Load dataset - Hugging Face will handle downloading if needed
    print(f"Loading Food-101 {split} split...")
    try:
        # Use default cache (None) to ensure fresh download if needed
        dataset = load_dataset("food101", split=split, cache_dir=cache_dir)
        print(f"✓ Loaded {len(dataset)} images")
        
        # Restore the backup directory if we renamed it
        if backup_dir and backup_dir.exists():
            if not local_food101_dir.exists():
                backup_dir.rename(local_food101_dir)
                print(f"   Restored {backup_dir} back to {local_food101_dir}")
        
        return dataset
    except Exception as e:
        # Restore the backup directory even if there's an error
        if backup_dir and backup_dir.exists():
            if not local_food101_dir.exists():
                backup_dir.rename(local_food101_dir)
                print(f"   Restored {backup_dir} back to {local_food101_dir}")
        
        # If we had LFS pointers, provide helpful error message
        if has_lfs_pointers:
            print(f"\n❌ Error: Could not load dataset.")
            print(f"   The local food101/ directory contains Git LFS pointer files.")
            print(f"   Solution options:")
            print(f"   1. Delete the food101/ directory: rm -rf {local_food101_dir}")
            print(f"   2. Or use Git LFS to pull actual files: git lfs pull")
            print(f"   3. Or download manually from Hugging Face")
        raise


def get_image_by_index(dataset, index):
    """
    Get a single image and its label by index.
    
    Args:
        dataset: The dataset object
        index: Index of the image (0 to len(dataset)-1)
    
    Returns:
        tuple: (PIL Image, label_index, label_name)
    """
    item = dataset[index]
    image = item['image']
    label_idx = item['label']
    
    # Get label name
    label_names = dataset.features['label'].names
    label_name = label_names[label_idx]
    
    return image, label_idx, label_name


def get_images_by_category(dataset, category_name):
    """
    Get all images of a specific food category.
    
    Args:
        dataset: The dataset object
        category_name: Name of the food category (e.g., "pizza", "hamburger")
    
    Returns:
        list: List of tuples (image, label_index, label_name)
    """
    label_names = dataset.features['label'].names
    
    if category_name not in label_names:
        raise ValueError(f"Category '{category_name}' not found. Available categories: {label_names[:10]}...")
    
    category_idx = label_names.index(category_name)
    
    # Filter images by category
    images = []
    for item in dataset:
        if item['label'] == category_idx:
            images.append((item['image'], item['label'], category_name))
    
    return images


def display_image_info(dataset, index):
    """
    Display information about an image.
    
    Args:
        dataset: The dataset object
        index: Index of the image
    """
    image, label_idx, label_name = get_image_by_index(dataset, index)
    
    print(f"\nImage Index: {index}")
    print(f"Category: {label_name} (ID: {label_idx})")
    print(f"Image Size: {image.size}")
    print(f"Image Mode: {image.mode}")
    print(f"Image Format: {image.format}")
    
    return image, label_idx, label_name


def save_image(image, output_path, label_name=None, index=None):
    """
    Save an image to disk.
    
    Args:
        image: PIL Image object
        output_path: Path to save the image
        label_name: Optional category name for folder organization
        index: Optional index for filename
    """
    output_path = Path(output_path)
    
    # Create directory if needed
    if label_name:
        output_path = output_path / label_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save image
    image.save(output_path)
    print(f"Saved image to: {output_path}")


def get_dataset_stats(dataset):
    """
    Get statistics about the dataset.
    
    Args:
        dataset: The dataset object
    
    Returns:
        dict: Dictionary with dataset statistics
    """
    label_names = dataset.features['label'].names
    
    # Count images per category
    from collections import Counter
    labels = [item['label'] for item in dataset]
    label_counts = Counter(labels)
    
    stats = {
        'total_images': len(dataset),
        'total_categories': len(label_names),
        'categories': label_names,
        'images_per_category': dict(label_counts),
        'min_images': min(label_counts.values()),
        'max_images': max(label_counts.values()),
        'avg_images': sum(label_counts.values()) / len(label_counts)
    }
    
    return stats


def print_dataset_stats(dataset):
    """Print dataset statistics in a readable format."""
    stats = get_dataset_stats(dataset)
    
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print(f"Total Images: {stats['total_images']}")
    print(f"Total Categories: {stats['total_categories']}")
    print(f"Images per Category:")
    print(f"  Min: {stats['min_images']}")
    print(f"  Max: {stats['max_images']}")
    print(f"  Average: {stats['avg_images']:.1f}")
    print("\nAll Categories:")
    for i, category in enumerate(stats['categories']):
        count = stats['images_per_category'][i]
        print(f"  {i:3d}: {category:30s} ({count} images)")


# Example usage functions
def example_basic_access():
    """Example: Basic image access."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Image Access")
    print("=" * 60)
    
    # Load training dataset
    dataset = load_dataset_from_cache(split="train")
    print(f"\nLoaded dataset with {len(dataset)} images")
    
    # Access first image
    image, label_idx, label_name = get_image_by_index(dataset, 0)
    print(f"\nFirst image:")
    print(f"  Category: {label_name}")
    print(f"  Label ID: {label_idx}")
    print(f"  Image Size: {image.size}")
    
    # Display image (uncomment to show)
    # image.show()
    
    return dataset


def example_access_multiple():
    """Example: Access multiple images."""
    print("\n" + "=" * 60)
    print("Example 2: Access Multiple Images")
    print("=" * 60)
    
    dataset = load_dataset_from_cache(split="train")
    
    print("\nFirst 5 images:")
    for i in range(5):
        image, label_idx, label_name = get_image_by_index(dataset, i)
        print(f"  [{i}] {label_name} - Size: {image.size}")
    
    return dataset


def example_filter_by_category():
    """Example: Filter images by category."""
    print("\n" + "=" * 60)
    print("Example 3: Filter by Category")
    print("=" * 60)
    
    dataset = load_dataset_from_cache(split="train")
    
    # Get all pizza images
    category = "pizza"
    pizza_images = get_images_by_category(dataset, category)
    
    print(f"\nFound {len(pizza_images)} images of '{category}'")
    if pizza_images:
        image, label_idx, label_name = pizza_images[0]
        print(f"First {category} image size: {image.size}")
        # image.show()  # Uncomment to display
    
    return pizza_images


def example_save_samples():
    """Example: Save sample images."""
    print("\n" + "=" * 60)
    print("Example 4: Save Sample Images")
    print("=" * 60)
    
    dataset = load_dataset_from_cache(split="train")
    output_dir = Path("sample_images")
    
    # Save first 10 images organized by category
    print(f"\nSaving first 10 images to {output_dir}/")
    for i in range(10):
        image, label_idx, label_name = get_image_by_index(dataset, i)
        filename = f"image_{i:04d}.jpg"
        save_image(image, output_dir / label_name / filename, label_name, i)
    
    print(f"\n✓ Images saved to {output_dir}/")
    return output_dir


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Access Food-101 dataset images")
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        choices=["train", "validation"],
        help="Dataset split to load (default: train)"
    )
    parser.add_argument(
        "--index",
        type=int,
        default=None,
        help="Display specific image by index"
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter images by category name (e.g., 'pizza', 'hamburger')"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show dataset statistics"
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Run example functions"
    )
    
    args = parser.parse_args()
    
    # Load dataset
    dataset = load_dataset_from_cache(split=args.split)
    
    # Show statistics
    if args.stats:
        print_dataset_stats(dataset)
    
    # Display specific image
    if args.index is not None:
        if 0 <= args.index < len(dataset):
            image, label_idx, label_name = display_image_info(dataset, args.index)
            print(f"\nTo display: image.show()")
        else:
            print(f"Error: Index {args.index} out of range (0-{len(dataset)-1})")
    
    # Filter by category
    if args.category:
        try:
            images = get_images_by_category(dataset, args.category)
            print(f"\nFound {len(images)} images of '{args.category}'")
            if images:
                image, label_idx, label_name = images[0]
                print(f"First image size: {image.size}")
        except ValueError as e:
            print(f"Error: {e}")
    
    # Run examples
    if args.examples:
        example_basic_access()
        example_access_multiple()
        example_filter_by_category()
        # Uncomment to save images
        # example_save_samples()
    
    # If no specific action, show quick help
    if not any([args.stats, args.index is not None, args.category, args.examples]):
        print("\n" + "=" * 60)
        print("Quick Usage Examples:")
        print("=" * 60)
        print("""
# In Python:
from access_images import load_dataset_from_cache, get_image_by_index

# Load dataset
dataset = load_dataset_from_cache(split="train")

# Get first image
image, label_idx, label_name = get_image_by_index(dataset, 0)
print(f"Category: {label_name}")
image.show()  # Display image

# Get all pizza images
from access_images import get_images_by_category
pizza_images = get_images_by_category(dataset, "pizza")
print(f"Found {len(pizza_images)} pizza images")

# Command line usage:
python access_images.py --stats                    # Show statistics
python access_images.py --index 0                  # Show image at index 0
python access_images.py --category pizza           # Find pizza images
python access_images.py --examples                 # Run all examples
        """)
