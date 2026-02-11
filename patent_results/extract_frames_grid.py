#!/usr/bin/env python3
"""
Extract all frames from temp.mov and create a labeled grid figure.
Each frame is labeled as "Frame 1", "Frame 2", etc.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

VIDEO_PATH = Path("/Users/leo/FoodProject/food-detection/patent_results/temp.mov")
OUTPUT_FILE = "FIGURE_temp_mov_frames.png"
# Specific frame indices to show (1-indexed, will be converted to 0-indexed)
FRAME_INDICES = [1, 5, 10, 15, 20, 25]  # 2x3 grid


def extract_specific_frames(video_path: Path, frame_indices: list[int], max_width: int = 600) -> list[np.ndarray]:
    """Extract specific frame indices from video (1-indexed), resized to max_width."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    
    # Get total frame count
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video has {total_frames} total frames")
    
    # Convert 1-indexed to 0-indexed and filter valid frames
    frame_indices_0based = [idx - 1 for idx in frame_indices if 1 <= idx <= total_frames]
    print(f"Extracting frames: {frame_indices} (0-indexed: {frame_indices_0based})")
    
    frames = []
    for idx_0based in frame_indices_0based:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx_0based)
        ret, frame_bgr = cap.read()
        if not ret:
            print(f"Warning: Could not read frame {idx_0based + 1}")
            continue
        
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        # Resize frame to reduce size
        h, w = frame_rgb.shape[:2]
        if w > max_width:
            scale = max_width / w
            new_h = int(h * scale)
            frame_rgb = cv2.resize(frame_rgb, (max_width, new_h), interpolation=cv2.INTER_AREA)
        
        frames.append(frame_rgb)
    
    cap.release()
    print(f"Extracted {len(frames)} frames")
    return frames


def create_grid_figure(frames: list[np.ndarray], output_path: Path, frame_indices: list[int] = None):
    """Create a grid figure with all frames labeled."""
    n_frames = len(frames)
    if n_frames == 0:
        print("[error] No frames to display")
        return
    
    # Calculate grid dimensions (2x3 for 6 frames)
    if n_frames == 6:
        cols = 3
        rows = 2
    else:
        # Roughly square for other counts
        cols = int(np.ceil(np.sqrt(n_frames)))
        rows = int(np.ceil(n_frames / cols))
    
    print(f"Creating {rows}x{cols} grid for {n_frames} frames...")
    
    # Set figure size based on grid (2.5 inches per frame for better visibility)
    fig_width = cols * 2.5
    fig_height = rows * 2.5
    plt.rcParams["figure.figsize"] = (fig_width, fig_height)
    plt.rcParams["figure.dpi"] = 150
    
    fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))
    
    # Handle single row/column cases
    if rows == 1:
        axes = axes.reshape(1, -1) if n_frames > 1 else np.array([[axes]])
    elif cols == 1:
        axes = axes.reshape(-1, 1) if n_frames > 1 else np.array([[axes]])
    
    # Flatten axes for easier indexing
    axes_flat = axes.flatten()
    
    # Use original frame indices for labels
    for idx, frame in enumerate(frames):
        ax = axes_flat[idx]
        ax.imshow(frame)
        ax.axis("off")
        # Label with the original 1-indexed frame number
        if frame_indices and idx < len(frame_indices):
            frame_number = frame_indices[idx]
        else:
            frame_number = idx + 1
        ax.set_title(f"Frame {frame_number}", fontsize=8, fontweight="bold")
    
    # Hide unused subplots
    for idx in range(n_frames, len(axes_flat)):
        axes_flat[idx].axis("off")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved grid figure: {output_path}")


def main():
    print(f"Extracting frames from: {VIDEO_PATH}")
    frames = extract_specific_frames(VIDEO_PATH, FRAME_INDICES)
    
    output_path = Path(__file__).parent / OUTPUT_FILE
    create_grid_figure(frames, output_path, FRAME_INDICES)


if __name__ == "__main__":
    main()
