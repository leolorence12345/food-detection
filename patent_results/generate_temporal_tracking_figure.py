#!/usr/bin/env python3
"""
Generate a temporal tracking figure with real SAM2 segmentations and IDs
from an existing video run (e.g., test.mov).

This script:
  - Reads detections from results.json (from run_pipeline.py on test.mov)
  - Tracks objects across frames via IoU to assign persistent IDs
  - Re-runs SAM2 on selected frames to get per-object masks
  - Builds a 1×N panel with SAM2-colored segments + ID labels
"""

import os
import sys
import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches, cm
import numpy as np
from PIL import Image

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

# Set this to the run corresponding to test.mov (created by run_pipeline.py)
RUN_ID = "run-64cf6bc5"

DOCKER_ROOT = Path("/Users/leo/FoodProject/food-detection/FoodAI/nutrition-video-analysis/terraform/docker")
OUTPUT_ROOT = DOCKER_ROOT / "data" / "outputs"
FRAMES_DIR = OUTPUT_ROOT / RUN_ID / "frames_temp"
RESULTS_PATH = DOCKER_ROOT / "results.json"

# Put app/ on sys.path so we can reuse Settings / ModelManager
sys.path.insert(0, str(DOCKER_ROOT))
from app.config import Settings
from app.models import ModelManager

# Which frame indices to show (0-based). Use all 15 processed frames (0–14) for a 5×3 grid.
FRAME_IDXS = list(range(0, 15))

OUTPUT_FILE = "FIGURE_temporal_tracking.png"


def load_img(path: str) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    return np.array(img)


def compute_iou(box1, box2):
    """Simple IoU for [x1,y1,x2,y2] boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter_w = max(0, x2 - x1)
    inter_h = max(0, y2 - y1)
    inter = inter_w * inter_h
    if inter == 0:
        return 0.0
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter
    return float(inter) / float(max(union, 1e-6))


def build_tracking_assignments(det_by_frame):
    """
    Build persistent IDs across selected frames using simple IoU tracking.
    Returns:
      frame_assignments: frame_idx -> list[{id,label,box}]
      id_to_color:       stable color per ID (for visual consistency)
    """
    tracked = {}  # id -> {"box": np.array, "label": str}
    next_id = 1
    frame_assignments = {}

    for idx in sorted(FRAME_IDXS):
        fd = det_by_frame.get(idx)
        if not fd:
            continue
        dets = [np.array(d["box"]) for d in fd.get("detections", [])]
        labels = [d["label"] for d in fd.get("detections", [])]

        assigned = {}
        used_ids = set()

        for di, box in enumerate(dets):
            best_iou = 0.0
            best_id = None
            for oid, obj in tracked.items():
                val = compute_iou(box, obj["box"])
                if val > best_iou:
                    best_iou = val
                    best_id = oid
            if best_id is not None and best_iou > 0.5 and best_id not in used_ids:
                assigned[di] = best_id
                used_ids.add(best_id)

        frame_items = []
        for di, box in enumerate(dets):
            raw_label = labels[di]
            if di in assigned:
                oid = assigned[di]
                tracked[oid]["box"] = box
                tracked[oid]["label"] = raw_label
            else:
                oid = next_id
                next_id += 1
                tracked[oid] = {"box": box, "label": raw_label}

            # For this figure, keep the raw Florence label (but we won't draw it)
            frame_items.append({"id": oid, "label": raw_label, "box": box})

        frame_assignments[idx] = frame_items

    # Stable colormap by ID
    palette = list(cm.get_cmap("tab10").colors)
    id_to_color = {}
    for items in frame_assignments.values():
        for item in items:
            oid = item["id"]
            if oid not in id_to_color:
                id_to_color[oid] = palette[len(id_to_color) % len(palette)]

    return frame_assignments, id_to_color


def build_sam2_masks(frame_assignments):
    """
    Run SAM2 on each selected frame using the tracked boxes as prompts.
    Returns:
      masks_by_frame: frame_idx -> list[{id,label,mask}]
    """
    config = Settings()
    config.DEVICE = os.environ.get("DEVICE", "cpu")

    # Mirror run_pipeline.py path fixes
    script_dir = DOCKER_ROOT
    config.OUTPUT_DIR = OUTPUT_ROOT
    config.UPLOAD_DIR = script_dir / "data" / "uploads"
    config.SAM2_CHECKPOINT = script_dir / "checkpoints" / "sam2.1_hiera_base_plus.pt"
    config.SAM2_CONFIG = script_dir / "sam2" / "configs" / "sam2.1" / "sam2.1_hiera_b+.yaml"

    model_manager = ModelManager(config)
    video_predictor = model_manager.sam2

    masks_by_frame = {}

    for idx in FRAME_IDXS:
        items = frame_assignments.get(idx, [])
        if not items:
            continue

        src_frame = FRAMES_DIR / f"{idx:05d}.jpg"
        if not src_frame.exists():
            continue

        # Create a tiny "video" directory with a single frame for SAM2
        tmp_dir = OUTPUT_ROOT / RUN_ID / f"sam2_tmp_{idx:05d}"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        dst_frame = tmp_dir / "00000.jpg"
        shutil.copy2(src_frame, dst_frame)

        inference_state = video_predictor.init_state(video_path=str(tmp_dir))

        frame_img = load_img(str(dst_frame))
        h, w = frame_img.shape[:2]

        # Add all detections as SAM2 tracked objects on frame_idx=0
        for i, item in enumerate(items):
            sam2_id = i + 1
            box = np.array(item["box"]).astype(float)
            x1, y1, x2, y2 = box
            # Clamp to frame bounds
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(x1 + 1, min(x2, w))
            y2 = max(y1 + 1, min(y2, h))
            box_sam = np.array([[[x1, y1], [x2, y2]]], dtype=float)

            video_predictor.add_new_points_or_box(
                inference_state=inference_state,
                frame_idx=0,
                obj_id=sam2_id,
                box=box_sam,
            )

        # Infer masks for this single frame
        out_frame_idx, sam2_obj_ids, out_mask_logits = video_predictor.infer_single_frame(
            inference_state, frame_idx=0
        )

        frame_masks = []
        for tensor_idx, sam2_id in enumerate(sam2_obj_ids):
            sam2_id_int = int(sam2_id)
            if sam2_id_int <= 0 or sam2_id_int > len(items):
                continue
            item = items[sam2_id_int - 1]
            logits = out_mask_logits[tensor_idx]
            mask_np = (logits > 0.0).cpu().numpy()
            if mask_np.ndim == 3:
                mask_np = mask_np[0]
            frame_masks.append(
                {
                    "id": item["id"],
                    "label": item["label"],
                    "mask": mask_np.astype(bool),
                }
            )

        masks_by_frame[idx] = frame_masks

    return masks_by_frame


def main():
    # Load detection results from the last pipeline run
    if not RESULTS_PATH.exists():
        print(f"[error] results.json not found at {RESULTS_PATH}")
        return

    with open(RESULTS_PATH, "r") as f:
        results = json.load(f)

    florence = results.get("florence_detections", [])
    det_by_frame = {fd["frame_idx"]: fd for fd in florence}

    # 1) Build temporal tracking IDs from Florence detections
    frame_assignments, id_to_color = build_tracking_assignments(det_by_frame)

    # 2) Run SAM2 on each selected frame to get real masks
    masks_by_frame = build_sam2_masks(frame_assignments)

    # 3) Load frames to visualize
    frames = []
    used_idxs = []
    for idx in FRAME_IDXS:
        frame_path = FRAMES_DIR / f"{idx:05d}.jpg"
        if frame_path.exists():
            frames.append(load_img(str(frame_path)))
            used_idxs.append(idx)

    if not frames:
        print("[error] no frames found for requested indices")
        return

    n = len(frames)
    # 5×3 grid (cols × rows) for up to 15 frames
    rows, cols = 3, 5
    plt.rcParams["figure.figsize"] = (4 * cols, 3 * rows)
    plt.rcParams["figure.dpi"] = 300

    fig, axes = plt.subplots(rows, cols)
    axes = np.array(axes)

    flat_axes = axes.flatten()

    for i, (idx, frame) in enumerate(zip(used_idxs, frames)):
        if i >= rows * cols:
            break
        ax = flat_axes[i]
        ax.imshow(frame)
        ax.axis("off")
        ax.set_title(f"Frame {idx}", fontsize=10, fontweight="bold")

        # Overlay SAM2 masks
        frame_masks = masks_by_frame.get(idx, [])
        for m in frame_masks:
            oid = m["id"]
            mask_bool = m["mask"]

            # Color derived only from stable ID; no text labels drawn
            base_color = id_to_color.get(oid, (1.0, 0.0, 0.0))

            h, w = mask_bool.shape
            colored = np.zeros((h, w, 4), dtype=float)
            colored[mask_bool] = [*base_color[:3], 0.45]
            ax.imshow(colored)

    # Turn off any unused subplots if we had fewer than 15 frames
    total_axes = rows * cols
    for j in range(i + 1, total_axes):
        flat_axes[j].axis("off")

    fig.suptitle(
        "Temporal tracking of food items across video frames (SAM2 segmentation)",
        fontsize=14,
        fontweight="bold",
    )

    out_path = Path(__file__).parent / OUTPUT_FILE
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved temporal tracking figure with SAM2: {out_path}")


if __name__ == "__main__":
    main()

