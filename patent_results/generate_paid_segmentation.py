#!/usr/bin/env python3
"""
Build a clean segmentation overlay for paid.jpg using REAL SAM2 masks.

We:
  - Load the original high-resolution paid.jpg
  - Load SAM2 per-object masks from run-5a38e919 (frame_00000_obj_*.png)
  - Resize masks to match paid.jpg resolution
  - Blend each mask onto the photo with a colormap
  - Output a single panel with only the colored segmentation (no labels)
"""

import os
import glob

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from PIL import Image

IMG_PATH = "/Users/leo/FoodProject/food-detection/paid.jpg"
RUN_ID = "run-5a38e919"  # SAM2 run for this image
BASE = "/Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker/data/outputs"
MASKS_DIR = os.path.join(BASE, RUN_ID, "masks")
FRAME_IDX = 0
OUTPUT_FILE = "FIGURE_paid_segmentation.png"


def build_overlay_on_photo(img: Image.Image, masks_dir: str, frame_idx: int):
    """Blend SAM2 masks onto the original photo with a color map."""
    base = np.array(img).astype(float) / 255.0
    h, w, _ = base.shape

    pattern = os.path.join(masks_dir, f"frame_{frame_idx:05d}_obj_*.png")
    mask_files = sorted(glob.glob(pattern))

    if not mask_files:
        print(f"[warn] No masks found for pattern: {pattern}")
        return (base * 255).astype(np.uint8)

    colors = cm.get_cmap("tab20", len(mask_files))(np.linspace(0, 1, len(mask_files)))
    overlay = base.copy()

    for mask_path, color in zip(mask_files, colors):
        try:
            m = Image.open(mask_path).convert("L")
            # Resize mask to match paid.jpg resolution
            m = m.resize((w, h), resample=Image.NEAREST)
            mask = np.array(m) > 0
        except Exception as e:
            print(f"[warn] could not load or resize mask {mask_path}: {e}")
            continue

        rgb = np.array(color[:3])
        alpha = 0.5
        overlay[mask] = (1 - alpha) * overlay[mask] + alpha * rgb

    return (overlay * 255).astype(np.uint8)


def main():
    img = Image.open(IMG_PATH).convert("RGB")
    overlay = build_overlay_on_photo(img, MASKS_DIR, FRAME_IDX)

    plt.rcParams["figure.figsize"] = (7, 4)
    plt.rcParams["figure.dpi"] = 300

    fig, ax = plt.subplots()
    ax.imshow(overlay)
    ax.axis("off")

    out_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    plt.tight_layout(pad=0)
    plt.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Saved segmentation figure on paid.jpg: {out_path}")


if __name__ == "__main__":
    main()



