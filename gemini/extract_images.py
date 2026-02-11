"""
Extract images from Food-101 dataset and save them to folders for easy browsing.

This script will create a directory structure with images organized by food category.
"""

from access_images import load_dataset_from_cache, get_image_by_index
from pathlib import Path
import argparse
from tqdm import tqdm


def extract_images(
    output_dir="food101_images",
    split="train",
    num_images_per_category=10,
    categories=None,
    start_index=0
):
    """
    Extract images from the dataset and save them to disk.
    
    Args:
        output_dir: Directory to save images
        split: Dataset split ("train" or "validation")
        num_images_per_category: Number of images to extract per category
        categories: List of category names to extract (None = all categories)
        start_index: Starting index for each category
    """
    print("=" * 60)
    print("Food-101 Image Extractor")
    print("=" * 60)
    
    # Load dataset
    print(f"\nLoading {split} split...")
    dataset = load_dataset_from_cache(split=split)
    label_names = dataset.features['label'].names
    print(f"✓ Loaded {len(dataset)} images")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Determine which categories to extract
    if categories is None:
        categories_to_extract = label_names
    else:
        # Validate categories
        invalid = [c for c in categories if c not in label_names]
        if invalid:
            print(f"⚠ Warning: Invalid categories: {invalid}")
        categories_to_extract = [c for c in categories if c in label_names]
    
    print(f"\nExtracting images from {len(categories_to_extract)} categories...")
    print(f"  Images per category: {num_images_per_category}")
    print(f"  Output directory: {output_path.resolve()}")
    
    # Extract images
    total_extracted = 0
    
    for category_name in tqdm(categories_to_extract, desc="Categories"):
        category_idx = label_names.index(category_name)
        
        # Create category directory
        category_dir = output_path / category_name
        category_dir.mkdir(exist_ok=True)
        
        # Find images of this category
        category_images = []
        for i in range(len(dataset)):
            if dataset[i]['label'] == category_idx:
                category_images.append(i)
        
        # Extract specified number of images
        images_to_extract = category_images[start_index:start_index + num_images_per_category]
        
        for img_idx in images_to_extract:
            try:
                image, label_idx, label_name = get_image_by_index(dataset, img_idx)
                
                # Save image
                filename = f"{category_name}_{img_idx:06d}.jpg"
                image_path = category_dir / filename
                image.save(image_path, "JPEG", quality=95)
                total_extracted += 1
            except Exception as e:
                print(f"\n⚠ Error extracting image {img_idx}: {e}")
                continue
    
    print(f"\n✓ Extracted {total_extracted} images")
    print(f"  Saved to: {output_path.resolve()}")
    print(f"\nYou can now browse the images in: {output_path}")
    
    return output_path


def extract_sample_images(output_dir="food101_sample_images", num_categories=10, num_images=5):
    """
    Extract a small sample of images for quick viewing.
    
    Args:
        output_dir: Directory to save images
        num_categories: Number of categories to sample
        num_images: Number of images per category
    """
    print("=" * 60)
    print("Food-101 Sample Image Extractor")
    print("=" * 60)
    
    # Load dataset
    print(f"\nLoading dataset...")
    dataset = load_dataset_from_cache(split="train")
    label_names = dataset.features['label'].names
    
    # Select first N categories
    categories = label_names[:num_categories]
    
    print(f"\nExtracting sample images:")
    print(f"  Categories: {num_categories}")
    print(f"  Images per category: {num_images}")
    
    return extract_images(
        output_dir=output_dir,
        split="train",
        num_images_per_category=num_images,
        categories=categories,
        start_index=0
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract images from Food-101 dataset")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="food101_images",
        help="Directory to save images (default: food101_images)"
    )
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        choices=["train", "validation"],
        help="Dataset split to extract (default: train)"
    )
    parser.add_argument(
        "--num-images",
        type=int,
        default=10,
        help="Number of images per category (default: 10)"
    )
    parser.add_argument(
        "--categories",
        type=str,
        nargs="+",
        default=None,
        help="Specific categories to extract (e.g., --categories pizza hamburger)"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Extract a small sample (10 categories, 5 images each)"
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Starting index for each category (default: 0)"
    )
    
    args = parser.parse_args()
    
    if args.sample:
        extract_sample_images(
            output_dir=args.output_dir,
            num_categories=10,
            num_images=5
        )
    else:
        extract_images(
            output_dir=args.output_dir,
            split=args.split,
            num_images_per_category=args.num_images,
            categories=args.categories,
            start_index=args.start_index
        )
