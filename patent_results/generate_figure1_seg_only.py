#!/usr/bin/env python3
"""
Generate a single-panel segmentation mask image for Example 1
using the real SAM2 masks from run-f00050ef.

This reuses the existing build_segmentation_overlay() from
generate_figure_1.py but outputs ONLY the colored segmentation
overlay without any text or brackets, suitable for the paper.
"""

import os
import matplotlib.pyplot as plt
import numpy as np

from generate_figure_1 import FRAME_PATH, MASKS_DIR, FRAME_IDX, build_segmentation_overlay, load_img

OUTPUT_FILE = "FIGURE_1_segmentation.png"


def main():
    # Load original frame and reconstruct segmentation overlay
    frame = load_img(FRAME_PATH)
    seg_img, _ = build_segmentation_overlay(frame, MASKS_DIR, FRAME_IDX)

    # Create single-panel figure with just the segmentation image
    plt.rcParams["figure.figsize"] = (7, 4)  # adjust as needed
    plt.rcParams["figure.dpi"] = 300

    fig, ax = plt.subplots()
    ax.imshow(np.array(seg_img))
    ax.axis("off")

    out_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    plt.tight_linewidth = 0.0
    plt.tight_layout(pad=0)
    plt.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Saved segmentation figure: {out_path}")


if __name__ == "__main__":
    main()

