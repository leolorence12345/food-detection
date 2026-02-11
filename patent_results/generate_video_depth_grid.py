#!/usr/bin/env python3
"""
Generate depth maps with SAM2 contours for frames from temp.mov and arrange in a 5x5 grid.

To run this script:
    cd /Users/leo/FoodProject/food-detection/patent_results
    source /Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker/venv/bin/activate
    python3 generate_video_depth_grid.py
"""

import os
import sys
from pathlib import Path

# Activate virtual environment by adding it to sys.path
DOCKER_ROOT = Path("/Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker")
VENV_PATH = DOCKER_ROOT / "venv"

# Add venv's site-packages to Python path
if VENV_PATH.exists():
    import sysconfig
    venv_site_packages = VENV_PATH / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    if venv_site_packages.exists():
        if str(venv_site_packages) not in sys.path:
            sys.path.insert(0, str(venv_site_packages))
    else:
        for alt_path in [VENV_PATH / "lib" / "site-packages", VENV_PATH / "lib64" / "site-packages"]:
            if alt_path.exists():
                if str(alt_path) not in sys.path:
                    sys.path.insert(0, str(alt_path))
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

VIDEO_PATH = Path("/Users/leo/FoodProject/food-detection/patent_results/temp.mov")
OUTPUT_FILE = "FIGURE_temp_mov_depth_grid.png"
NUM_FRAMES = 25  # 5x5 grid
MAX_IMAGE_WIDTH = 400  # Smaller for grid display
GRID_ROWS = 5
GRID_COLS = 5


def estimate_depth_metric3d(frame_np, model, device):
    """Estimate depth using Metric3D (returns meters)"""
    try:
        rgb_input = torch.from_numpy(frame_np).permute(2, 0, 1).unsqueeze(0).float().to(device)
        
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        with torch.no_grad():
            pred_depth, confidence, output_dict = model.inference({'input': rgb_input})
        
        depth_map_meters = pred_depth.squeeze().cpu().numpy()
        
        del rgb_input, pred_depth, confidence, output_dict
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        if depth_map_meters.shape != frame_np.shape[:2]:
            depth_map_meters = cv2.resize(
                depth_map_meters, (frame_np.shape[1], frame_np.shape[0]),
                interpolation=cv2.INTER_LINEAR
            )
        
        return depth_map_meters
    except Exception as e:
        print(f"[error] Depth estimation failed: {e}")
        raise


def get_sam2_contours(image_rgb, generator):
    """Get SAM2 segmentation contours for an image."""
    masks = generator.generate(image_rgb)
    
    contours = []
    for mask_data in masks:
        mask = mask_data['segmentation']
        mask_uint8 = (mask * 255).astype(np.uint8)
        cnts, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours.extend(cnts)
    
    return contours


def visualize_depth_with_contours(depth_map, contours, vmin, vmax):
    """Create a depth map visualization with contours overlaid."""
    fig, ax = plt.subplots(1, 1, figsize=(4, 4))
    
    im = ax.imshow(depth_map, cmap='plasma', vmin=vmin, vmax=vmax)
    
    # Overlay contours
    if contours:
        for contour in contours:
            if len(contour.shape) == 3 and contour.shape[1] == 1:
                contour_plot = contour.reshape(-1, 2)
            else:
                contour_plot = contour
            if len(contour_plot) > 0:
                ax.plot(contour_plot[:, 0], contour_plot[:, 1], 
                        color='white', linewidth=0.5, alpha=0.4)
    
    ax.axis("off")
    
    # Save to buffer
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)
    
    return buf


def extract_video_frames(video_path, num_frames):
    """Extract evenly spaced frames from video. Returns frames and their 1-indexed frame numbers."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video has {total_frames} frames")
    
    # Calculate frame indices to extract (0-indexed)
    # Use a more conservative range to avoid edge cases
    frame_indices_0based = np.linspace(0, total_frames - 2, num_frames, dtype=int)
    
    frames = []
    frame_numbers = []  # 1-indexed frame numbers for labeling
    
    for idx_0based in frame_indices_0based:
        # Try the target frame first
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx_0based)
        ret, frame = cap.read()
        
        if not ret:
            # If target frame fails, try nearby frames
            found = False
            for offset in [1, -1, 2, -2, 3, -3]:  # Try nearby frames
                try_idx = max(0, min(idx_0based + offset, total_frames - 1))
                cap.set(cv2.CAP_PROP_POS_FRAMES, try_idx)
                ret, frame = cap.read()
                if ret:
                    idx_0based = try_idx  # Update to the frame we actually read
                    found = True
                    break
            
            if not found:
                print(f"[warning] Could not read frame {idx_0based} or nearby frames, skipping...")
                continue
        
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Resize to reduce memory
            h, w = frame_rgb.shape[:2]
            if w > MAX_IMAGE_WIDTH:
                scale = MAX_IMAGE_WIDTH / w
                new_h = int(h * scale)
                frame_rgb = cv2.resize(frame_rgb, (MAX_IMAGE_WIDTH, new_h), interpolation=cv2.INTER_AREA)
            frames.append(frame_rgb)
            frame_numbers.append(idx_0based + 1)  # Convert to 1-indexed
    
    cap.release()
    print(f"Extracted {len(frames)} frames")
    
    # If we still don't have enough frames, try to fill from the beginning
    if len(frames) < num_frames:
        print(f"[warning] Only extracted {len(frames)} frames, trying to get more...")
        cap = cv2.VideoCapture(str(video_path))
        # Try reading frames sequentially from the start
        for frame_idx in range(total_frames):
            if len(frames) >= num_frames:
                break
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                # Check if we already have this frame
                if (frame_idx + 1) not in frame_numbers:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w = frame_rgb.shape[:2]
                    if w > MAX_IMAGE_WIDTH:
                        scale = MAX_IMAGE_WIDTH / w
                        new_h = int(h * scale)
                        frame_rgb = cv2.resize(frame_rgb, (MAX_IMAGE_WIDTH, new_h), interpolation=cv2.INTER_AREA)
                    frames.append(frame_rgb)
                    frame_numbers.append(frame_idx + 1)
        cap.release()
    
    print(f"Final count: {len(frames)} frames extracted")
    
    if len(frames) < num_frames:
        print(f"[warning] Only extracted {len(frames)} frames, expected {num_frames}")
    
    return frames, frame_numbers


def main():
    device = os.environ.get("DEVICE", "cpu")
    print(f"Using device: {device}")
    
    # Load video and extract frames
    print(f"\nExtracting frames from: {VIDEO_PATH}")
    frames, frame_numbers = extract_video_frames(VIDEO_PATH, NUM_FRAMES)
    
    if len(frames) == 0:
        print("[error] No frames extracted!")
        return
    
    if len(frames) < NUM_FRAMES:
        print(f"[error] Only extracted {len(frames)} frames, need {NUM_FRAMES} for {GRID_ROWS}x{GRID_COLS} grid")
        return
    
    # Load models
    print("\nLoading Metric3D model...")
    config = Settings()
    metric3d_model = load_metric3d(model_name=config.METRIC3D_MODEL, device=device)
    print("✓ Metric3D loaded")
    
    print("\nLoading SAM2 model...")
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
    
    sam2_generator = SAM2AutomaticMaskGenerator(
        sam_model,
        points_per_side=32,
        pred_iou_thresh=0.8,
        stability_score_thresh=0.95,
        crop_n_layers=0,
        min_mask_region_area=100,
        output_mode="binary_mask",
    )
    print("✓ SAM2 loaded")
    
    # Process each frame (ensure we process exactly NUM_FRAMES)
    frames_to_process = frames[:NUM_FRAMES]  # Take exactly NUM_FRAMES
    frame_numbers_to_process = frame_numbers[:NUM_FRAMES]
    
    print(f"\nProcessing {len(frames_to_process)} frames...")
    depth_visualizations = []
    all_depths = []
    
    for i, frame in enumerate(frames_to_process):
        print(f"  Processing frame {i+1}/{len(frames_to_process)} (Frame {frame_numbers_to_process[i]})...")
        
        # Estimate depth
        depth_map = estimate_depth_metric3d(frame, metric3d_model, device)
        all_depths.append(depth_map)
        
        # Get SAM2 contours
        contours = get_sam2_contours(frame, sam2_generator)
        
        depth_visualizations.append((depth_map, contours))
    
    # Calculate global depth range for consistent colormap
    all_depths_array = np.concatenate([d.flatten() for d in all_depths])
    valid_depths = all_depths_array[all_depths_array > 0]
    if len(valid_depths) > 0:
        vmin = np.percentile(valid_depths, 2)
        vmax = np.percentile(valid_depths, 98)
    else:
        vmin = None
        vmax = None
    
    print(f"\nGlobal depth range: {vmin:.3f}m to {vmax:.3f}m")
    
    # Create grid visualization
    print("\nCreating grid visualization...")
    fig, axes = plt.subplots(GRID_ROWS, GRID_COLS, figsize=(20, 20))
    axes = axes.flatten()
    
    for idx, (depth_map, contours) in enumerate(depth_visualizations):
        ax = axes[idx]
        
        if vmin is not None and vmax is not None:
            im = ax.imshow(depth_map, cmap='plasma', vmin=vmin, vmax=vmax)
        else:
            im = ax.imshow(depth_map, cmap='plasma')
        
        # Overlay contours
        if contours:
            for contour in contours:
                if len(contour.shape) == 3 and contour.shape[1] == 1:
                    contour_plot = contour.reshape(-1, 2)
                else:
                    contour_plot = contour
                if len(contour_plot) > 0:
                    ax.plot(contour_plot[:, 0], contour_plot[:, 1], 
                            color='white', linewidth=0.5, alpha=0.4)
        
        # Add frame label (sequential 1-25, not actual video frame numbers)
        ax.set_title(f"Frame {idx + 1}", fontsize=10, fontweight="bold", pad=5)
        ax.axis("off")
    
    # Hide unused subplots
    for idx in range(len(depth_visualizations), len(axes)):
        axes[idx].axis("off")
    
    plt.tight_layout(pad=0.5)
    output_path = Path(__file__).parent / OUTPUT_FILE
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"✓ Saved grid visualization: {output_path}")


if __name__ == "__main__":
    main()
