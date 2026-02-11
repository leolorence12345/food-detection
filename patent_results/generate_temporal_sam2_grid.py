#!/usr/bin/env python3
"""
Pure SAM2 auto-segmentation over video frames (no Florence prompts, no labels).

This script:
  - Loads the SAM2 base model from the same checkpoint/config as the pipeline
  - Reads frames directly from test.mov
  - Runs SAM2AutomaticMaskGenerator per frame (SAM2-D style auto masks)
  - Builds a 5×3 grid (15 frames) with colored SAM2 masks and no text
"""

import os
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt

# Make sure we can import the local sam2 package under docker/
import sys
DOCKER_ROOT = Path("/Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker")
if str(DOCKER_ROOT) not in sys.path:
    sys.path.insert(0, str(DOCKER_ROOT))

from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

VIDEO_PATH = Path("/Users/leo/FoodProject/food-detection/test.mov")


def load_sam2_auto_generator(device: str = "cpu") -> SAM2AutomaticMaskGenerator:
    """Load SAM2 base model + automatic mask generator (no prompts)."""
    # Mirror how config paths are set in Settings / run_pipeline.py
    ckpt_path = DOCKER_ROOT / "checkpoints" / "sam2.1_hiera_base_plus.pt"
    cfg_abs = DOCKER_ROOT / "sam2" / "configs" / "sam2.1" / "sam2.1_hiera_b+.yaml"

    # Build config_name relative to sam2 package root, as in app.models.load_sam2
    import sam2
    from pathlib import Path as PathLib

    sam2_root = PathLib(sam2.__path__[0])
    try:
        config_file_str = str(cfg_abs.relative_to(sam2_root)).replace(os.sep, "/")
    except ValueError:
        # Fallback: try splitting on sam2_root segment
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

    # Default AMG settings taken from upstream SAM2
    generator = SAM2AutomaticMaskGenerator(
        sam_model,
        points_per_side=32,
        pred_iou_thresh=0.8,
        stability_score_thresh=0.95,
        crop_n_layers=0,
        crop_n_points_downscale_factor=1,
        min_mask_region_area=0,
        output_mode="binary_mask",
    )
    return generator


def sample_video_frames(video_path: Path, max_frames: int = 15) -> list[np.ndarray]:
    """Read first N frames from the video as RGB numpy arrays."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    frames = []
    while len(frames) < max_frames:
        ret, frame_bgr = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)

    cap.release()
    return frames


def build_sam2_grid():
    device = os.environ.get("DEVICE", "cpu")
    gen = load_sam2_auto_generator(device=device)

    frames = sample_video_frames(VIDEO_PATH, max_frames=15)
    if not frames:
        print(f"[error] no frames read from {VIDEO_PATH}")
        return

    rows, cols = 3, 5
    n = min(len(frames), rows * cols)

    plt.rcParams["figure.figsize"] = (4 * cols, 3 * rows)
    plt.rcParams["figure.dpi"] = 300

    fig, axes = plt.subplots(rows, cols)
    axes = np.array(axes)
    flat_axes = axes.flatten()

    cmap = plt.get_cmap("tab20")

    for i in range(n):
        frame = frames[i]
        ax = flat_axes[i]
        ax.imshow(frame)
        ax.axis("off")
        ax.set_title(f"Frame {i}", fontsize=8)

        # Pure SAM2 auto masks (no prompts)
        masks = gen.generate(frame)
        # Each entry: {"segmentation": mask, "area": ..., "bbox": ..., "predicted_iou": ...}
        for j, m in enumerate(masks):
            mask = m["segmentation"]
            color = cmap(j % cmap.N)
            h, w = mask.shape
            overlay = np.zeros((h, w, 4), dtype=float)
            overlay[mask.astype(bool)] = [*color[:3], 0.5]
            ax.imshow(overlay)

    # Hide unused axes if fewer than 15 frames
    for j in range(n, rows * cols):
        flat_axes[j].axis("off")

    fig.suptitle("Pure SAM2 auto-segmentation over video frames (5×3 grid)", fontsize=14, fontweight="bold")
    out_path = Path(__file__).parent / "FIGURE_temporal_sam2_grid.png"
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved pure SAM2 grid figure: {out_path}")


if __name__ == "__main__":
    build_sam2_grid()

