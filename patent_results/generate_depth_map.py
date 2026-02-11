#!/usr/bin/env python3
"""
Generate a depth map for paid.jpg using Metric3D.

To run this script:
    cd /Users/leo/FoodProject/food-detection/patent_results
    source /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker/venv/bin/activate
    python3 generate_depth_map.py

Or run directly (script will auto-detect venv):
    cd /Users/leo/FoodProject/food-detection/patent_results
    python3 generate_depth_map.py
"""

import os
import sys
from pathlib import Path

# Activate virtual environment by adding it to sys.path
DOCKER_ROOT = Path("/Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker")
VENV_PATH = DOCKER_ROOT / "venv"

# Add venv's site-packages to Python path
if VENV_PATH.exists():
    # Find site-packages directory (works for both regular venv and conda-style)
    import sysconfig
    venv_site_packages = VENV_PATH / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    if venv_site_packages.exists():
        if str(venv_site_packages) not in sys.path:
            sys.path.insert(0, str(venv_site_packages))
            print(f"✓ Added venv site-packages to path: {venv_site_packages}")
    else:
        # Try alternative paths
        for alt_path in [VENV_PATH / "lib" / "site-packages", VENV_PATH / "lib64" / "site-packages"]:
            if alt_path.exists():
                if str(alt_path) not in sys.path:
                    sys.path.insert(0, str(alt_path))
                    print(f"✓ Added venv site-packages to path: {alt_path}")
                break

# Add app directory to path
if str(DOCKER_ROOT) not in sys.path:
    sys.path.insert(0, str(DOCKER_ROOT))

import cv2
import numpy as np
import matplotlib.pyplot as plt
import torch

from app.models import load_metric3d
from app.config import Settings
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

IMAGE_PATH = Path("/Users/leo/FoodProject/food-detection/paid.jpg")
OUTPUT_FILE = "FIGURE_paid_depth_map.png"
MAX_IMAGE_WIDTH = 800  # Resize large images to reduce memory usage


def estimate_depth_metric3d(frame_np, model, device):
    """Estimate depth using Metric3D (returns meters)"""
    try:
        print(f"  Input shape: {frame_np.shape}")
        rgb_input = torch.from_numpy(frame_np).permute(2, 0, 1).unsqueeze(0).float().to(device)
        print(f"  Tensor shape: {rgb_input.shape}, device: {rgb_input.device}")
        
        # Clear cache before inference
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print("  Running Metric3D inference...")
        with torch.no_grad():
            pred_depth, confidence, output_dict = model.inference({'input': rgb_input})
        
        print(f"  Raw depth output shape: {pred_depth.shape}")
        depth_map_meters = pred_depth.squeeze().cpu().numpy()
        print(f"  Depth map shape: {depth_map_meters.shape}")
        print(f"  Depth map dtype: {depth_map_meters.dtype}")
        print(f"  Depth range (raw): {depth_map_meters.min():.4f}m to {depth_map_meters.max():.4f}m")
        
        # Clean up GPU memory
        del rgb_input, pred_depth, confidence, output_dict
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Resize if needed (shouldn't be needed if we resized input)
        if depth_map_meters.shape != frame_np.shape[:2]:
            depth_map_meters = cv2.resize(
                depth_map_meters, (frame_np.shape[1], frame_np.shape[0]),
                interpolation=cv2.INTER_LINEAR
            )
        
        return depth_map_meters
    except Exception as e:
        print(f"[error] Depth estimation failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def get_sam2_segmentation_contours(image_rgb, device):
    """Get SAM2 automatic segmentation masks and extract contours."""
    print("\nRunning SAM2 automatic segmentation...")
    
    # Load SAM2 auto generator
    ckpt_path = DOCKER_ROOT / "checkpoints" / "sam2.1_hiera_base_plus.pt"
    cfg_abs = DOCKER_ROOT / "sam2" / "configs" / "sam2.1" / "sam2.1_hiera_b+.yaml"
    
    import sam2
    from pathlib import Path as PathLib
    sam2_root = PathLib(sam2.__path__[0])
    
    try:
        config_file_str = str(cfg_abs.relative_to(sam2_root)).replace(os.sep, "/")
    except ValueError:
        cfg_str = str(cfg_abs.resolve())
        sam2_str = str(sam2_root.resolve())
        if sam2_str in cfg_str:
            config_file_str = cfg_str.split(sam2_str + os.sep, 1)[1].replace(os.sep, "/")
        else:
            config_file_str = str(cfg_abs)
    
    sam_model = build_sam2(
        config_file=config_file_str,
        ckpt_path=str(ckpt_path),
        device=device,
        mode="eval",
        apply_postprocessing=True,
    )
    
    generator = SAM2AutomaticMaskGenerator(
        sam_model,
        points_per_side=32,
        pred_iou_thresh=0.8,
        stability_score_thresh=0.95,
        crop_n_layers=0,
        min_mask_region_area=100,  # Filter out tiny masks
        output_mode="binary_mask",
    )
    
    print("  Generating masks...")
    masks = generator.generate(image_rgb)
    print(f"  Generated {len(masks)} masks")
    
    # Extract contours from masks
    contours = []
    for mask_data in masks:
        mask = mask_data['segmentation']  # Boolean array
        # Convert to uint8 for cv2.findContours
        mask_uint8 = (mask * 255).astype(np.uint8)
        # Find contours
        cnts, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours.extend(cnts)
    
    print(f"  Extracted {len(contours)} contours")
    return contours


def visualize_depth_map(image, depth_map, output_path, contours=None):
    """Create a visualization of depth map with enhanced contrast."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Depth map with enhanced contrast
    # Filter out invalid depths (0 or negative)
    valid_depths = depth_map[depth_map > 0]
    if len(valid_depths) > 0:
        # Use percentile-based normalization for better contrast
        # This ensures we see the depth differences (burger vs plate vs table)
        vmin = np.percentile(valid_depths, 2)  # 2nd percentile (closest objects)
        vmax = np.percentile(valid_depths, 98)  # 98th percentile (farthest objects)
        
        print(f"Depth statistics:")
        print(f"  Min (closest): {vmin:.3f}m")
        print(f"  Max (farthest): {vmax:.3f}m")
        print(f"  Range: {vmax - vmin:.3f}m")
        print(f"  This should show: burger (closer) > plate (middle) > table (farther)")
        
        # Use 'plasma' or 'inferno' colormap - closer objects are brighter/yellow, farther are darker/purple
        # This makes it intuitive: bright = close, dark = far
        im = ax.imshow(depth_map, cmap='plasma', vmin=vmin, vmax=vmax)
    else:
        print("[warning] No valid depth values found!")
        im = ax.imshow(depth_map, cmap='plasma')
    
    # Overlay SAM2 segmentation contours faintly
    if contours:
        print(f"  Drawing {len(contours)} contours on depth map...")
        # Convert to matplotlib format and draw faintly
        for contour in contours:
            # Reshape contour for matplotlib: (N, 1, 2) -> (N, 2)
            if len(contour.shape) == 3 and contour.shape[1] == 1:
                contour_plot = contour.reshape(-1, 2)
            else:
                contour_plot = contour
            # Ensure we have valid coordinates
            if len(contour_plot) > 0:
                # Draw with faint white/light color, thin line
                # Note: cv2 coordinates are (x, y), matplotlib expects (x, y) so we're good
                ax.plot(contour_plot[:, 0], contour_plot[:, 1], 
                            color='white', linewidth=0.8, alpha=0.4)
    
    ax.axis("off")
    # No title for depth map
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Depth", fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved depth map visualization: {output_path}")


def main():
    device = os.environ.get("DEVICE", "cpu")
    print(f"Using device: {device}")
    
    # Load image
    if not IMAGE_PATH.exists():
        print(f"[error] Image not found: {IMAGE_PATH}")
        return
    
    print(f"Loading image: {IMAGE_PATH}")
    image_bgr = cv2.imread(str(IMAGE_PATH))
    if image_bgr is None:
        print(f"[error] Could not load image: {IMAGE_PATH}")
        return
    
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    original_shape = image_rgb.shape
    print(f"Original image shape: {image_rgb.shape}")
    
    # Resize image if too large to reduce memory usage
    h, w = image_rgb.shape[:2]
    if w > MAX_IMAGE_WIDTH:
        scale = MAX_IMAGE_WIDTH / w
        new_h = int(h * scale)
        print(f"Resizing image to {MAX_IMAGE_WIDTH}x{new_h} to reduce memory usage...")
        image_rgb = cv2.resize(image_rgb, (MAX_IMAGE_WIDTH, new_h), interpolation=cv2.INTER_AREA)
        print(f"Resized image shape: {image_rgb.shape}")
    
    # Load Metric3D model
    print("\nLoading Metric3D model...")
    config = Settings()
    print(f"  Model name: {config.METRIC3D_MODEL}")
    print(f"  Device: {device}")
    metric3d_model = load_metric3d(model_name=config.METRIC3D_MODEL, device=device)
    print("✓ Metric3D model loaded")
    print(f"  Model type: {type(metric3d_model)}")
    print(f"  Model has 'inference' method: {hasattr(metric3d_model, 'inference')}")
    if hasattr(metric3d_model, 'inference'):
        print("  ✓ This is the real Metric3D model (has inference method)")
    
    # Estimate depth
    print("\nEstimating depth map...")
    print("This may take a moment and use significant memory...")
    try:
        depth_map = estimate_depth_metric3d(image_rgb, metric3d_model, device)
        print(f"✓ Depth map estimated")
        print(f"Depth map shape: {depth_map.shape}")
        print(f"Depth range: {depth_map.min():.3f}m to {depth_map.max():.3f}m")
        
        # Get SAM2 segmentation contours
        contours = None
        try:
            contours = get_sam2_segmentation_contours(image_rgb, device)
            print("✓ SAM2 segmentation complete")
        except Exception as e:
            print(f"[warning] SAM2 segmentation failed: {e}")
            print("  Continuing without segmentation contours...")
            import traceback
            traceback.print_exc()
        
        # Visualize and save
        output_path = Path(__file__).parent / OUTPUT_FILE
        visualize_depth_map(image_rgb, depth_map, output_path, contours)
        print("✓ Complete!")
    except MemoryError:
        print(f"\n[error] Out of memory! Try:")
        print(f"  1. Reduce MAX_IMAGE_WIDTH in the script (currently {MAX_IMAGE_WIDTH})")
        print(f"  2. Close other applications to free memory")
        print(f"  3. Use a smaller image")
        raise
    except Exception as e:
        print(f"\n[error] Failed to generate depth map: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
