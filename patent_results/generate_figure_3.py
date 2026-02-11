#!/usr/bin/env python3
"""
Generate Figure 3: Handling Partial Occlusion with Ingredient Preservation
Patent Example 3
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
DPI = 300
FIGSIZE = (12, 14)  # 12" x 14" portrait
OUTPUT_FILE = "Figure_3_Partial_Occlusion.png"

def create_sandwich_image(width, height, occlusion_level, frame_num):
    """Create sandwich image with varying occlusion"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')
    
    center_x, center_y = width // 2, height // 2
    
    # Draw plate
    draw.ellipse([center_x-140, center_y+40, center_x+140, center_y+60],
                outline='gray', width=2)
    
    # Draw sandwich (layered)
    sandwich_left = center_x - 80
    sandwich_right = center_x + 80
    sandwich_top = center_y - 50
    sandwich_bottom = center_y + 40
    
    # Bottom bread
    draw.rectangle([sandwich_left, sandwich_bottom-10, sandwich_right, sandwich_bottom],
                  fill='#D2691E', outline='#8B4513', width=2)
    
    # Lettuce (green)
    draw.rectangle([sandwich_left-5, sandwich_bottom-20, sandwich_right+5, sandwich_bottom-10],
                  fill='#90EE90', outline='#228B22', width=1)
    
    # Tomato (red)
    draw.ellipse([sandwich_left+10, sandwich_bottom-35, sandwich_left+50, sandwich_bottom-20],
                fill='#FF6347', outline='#DC143C', width=1)
    
    # Cheese (yellow)
    draw.rectangle([sandwich_left+5, sandwich_bottom-42, sandwich_right-5, sandwich_bottom-35],
                  fill='#FFD700', outline='#DAA520', width=1)
    
    # Turkey (pink)
    draw.rectangle([sandwich_left+10, sandwich_bottom-50, sandwich_right-10, sandwich_bottom-42],
                  fill='#FFC0CB', outline='#FF69B4', width=1)
    
    # Top bread
    draw.arc([sandwich_left, sandwich_top, sandwich_right, sandwich_bottom-45],
            start=0, end=180, fill='#D2691E', width=3)
    draw.chord([sandwich_left, sandwich_top, sandwich_right, sandwich_bottom-45],
              start=0, end=180, fill='#D2691E', outline='#8B4513', width=2)
    
    # Add occlusion overlay
    if occlusion_level == 50:
        # 50% occluded - hand covering top half
        draw.ellipse([center_x+20, center_y-80, center_x+120, center_y+20],
                    fill=(255, 220, 177, 200), outline='peru', width=3)
        draw.text((center_x+50, center_y-50), '✋', font=None)
        draw.text((10, height-40), "50% Occluded", fill='red', font=None)
    elif occlusion_level == 75:
        # 75% occluded - hand + napkin
        draw.ellipse([center_x+10, center_y-90, center_x+130, center_y+30],
                    fill=(255, 220, 177, 220), outline='peru', width=3)
        draw.rectangle([center_x-60, center_y-70, center_x+40, center_y-20],
                      fill=(255, 255, 255, 200), outline='gray', width=2)
        draw.text((center_x+55, center_y-45), '✋', font=None)
        draw.text((center_x-30, center_y-50), 'Napkin', fill='gray', font=None)
        draw.text((10, height-40), "75% Occluded", fill='darkred', font=None)
    else:
        draw.text((10, height-40), "Unoccluded", fill='green', font=None)
    
    # Frame number
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), f"Frame {frame_num}", fill='black', font=font)
    
    return np.array(img)

def create_segmentation_mask(width, height, visibility, frame_num):
    """Create segmentation mask with visibility indicator"""
    img = Image.new('RGB', (width, height), '#F0F0F0')
    draw = ImageDraw.Draw(img, 'RGBA')
    
    center_x, center_y = width // 2, height // 2
    
    # Segmentation mask (green, varying opacity based on visibility)
    if visibility == 100:
        alpha = 150
        mask_color = (0, 255, 0, alpha)
        draw.rectangle([center_x-80, center_y-50, center_x+80, center_y+40],
                      fill=mask_color, outline='green', width=4)
    elif visibility == 50:
        alpha = 100
        mask_color = (0, 255, 0, alpha)
        draw.rectangle([center_x-80, center_y, center_x+80, center_y+40],
                      fill=mask_color, outline='green', width=4)
    else:  # 25%
        alpha = 80
        mask_color = (0, 255, 0, alpha)
        draw.rectangle([center_x+40, center_y+10, center_x+80, center_y+40],
                      fill=mask_color, outline='green', width=4)
    
    # ID label
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    draw.text((center_x-20, center_y+5), "ID: 1", fill='white', font=font,
             stroke_width=2, stroke_fill='black')
    
    # Visibility indicator
    draw.text((10, 10), f"Frame {frame_num}", fill='black', font=small_font)
    draw.text((10, height-35), f"Visibility: {visibility}%", fill='blue', font=small_font)
    
    return np.array(img)

def main():
    """Generate Figure 3"""
    print("Generating Figure 3: Partial Occlusion...")
    
    # Create figure
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.5, wspace=0.3,
                          top=0.95, bottom=0.05, left=0.05, right=0.95)
    
    # Title
    fig.suptitle('FIGURE 3: Handling Partial Occlusion with Ingredient Preservation\nPatent Example 3',
                fontsize=16, fontweight='bold')
    
    # Row 1: Original frames (A-D)
    frames = [2, 6, 10, 14]
    occlusions = [0, 50, 75, 0]
    descriptions = ['Unoccluded', 'Partial (50%)', 'Heavy (75%)', 'Unoccluded']
    
    for i, (frame, occ, desc) in enumerate(zip(frames, occlusions, descriptions)):
        ax = fig.add_subplot(gs[0, i])
        img = create_sandwich_image(350, 300, occ, frame)
        ax.imshow(img)
        ax.set_title(f'({chr(65+i)}) Frame {frame}\n{desc}', fontsize=9, fontweight='bold')
        ax.axis('off')
    
    # Row 2: Segmentation masks (E-G) + Tracking table (H)
    visibilities = [100, 50, 25, 100]
    
    for i in range(3):
        ax = fig.add_subplot(gs[1, i])
        img = create_segmentation_mask(350, 300, visibilities[i], frames[i])
        ax.imshow(img)
        ax.set_title(f'({chr(69+i)}) Segmentation\nFrame {frames[i]}', fontsize=9, fontweight='bold')
        ax.axis('off')
    
    # Tracking table
    ax = fig.add_subplot(gs[1, 3])
    ax.axis('off')
    
    tracking_text = """
(H) Ingredient Tracking

Frame │ Visibility│ Status
──────┼───────────┼────────
  2   │   100%    │ ✓ ALL 6
      │           │ DETECTED
      │           │ • Bread×2
      │           │ • Turkey
      │           │ • Cheese
      │           │ • Lettuce
      │           │ • Tomato
      │           │ → STORED
──────┼───────────┼────────
  6   │    50%    │ ✓ KEPT
      │           │ from memory
──────┼───────────┼────────
 10   │    25%    │ ✓ KEPT
      │           │ from memory
──────┼───────────┼────────
 14   │   100%    │ ✓ Validated
      │           │ correct ✓
"""
    
    ax.text(0.05, 0.95, tracking_text, fontsize=7, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.4))
    
    # Row 3: Ingredient Preservation (I) - Full width
    ax = fig.add_subplot(gs[2, :])
    ax.axis('off')
    
    preservation_text = """
(I) INGREDIENT-LEVEL DESCRIPTION PRESERVATION

Object #1: "Turkey & Cheese Sandwich" (ID persists across Frames 0-20)

┌─────────────────────────────────────────────────────────────────────────────────┐
│ Frame 2 (Unoccluded): FULL ingredient detection                                │
│ ──────────────────────────────────────────────────────────────────────────────  │
│   Detected Ingredients: Whole wheat bread (2 slices), Turkey slices (3-4),     │
│   Cheddar cheese (2 slices), Lettuce (green leaves), Tomato (2 slices),        │
│   Mayonnaise (white spread)                                                     │
│   → STORED in object memory for ID #1                                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ Frame 6 (50% Occluded by hand): PARTIAL visibility                             │
│ ──────────────────────────────────────────────────────────────────────────────  │
│   Visible: Bottom bread, Lettuce edge                                           │
│   Occluded: Turkey, Cheese, Top bread                                           │
│   → RETAINED from Frame 2 (ingredient memory) - Same Object ID #1               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ Frame 10 (75% Occluded): MINIMAL visibility                                    │
│ ──────────────────────────────────────────────────────────────────────────────  │
│   Visible: Small portion of bread edge only                                     │
│   → ALL 6 ingredients preserved from Frame 2 - No information loss              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ Frame 14 (Unoccluded again): Confirms preservation                             │
│ ──────────────────────────────────────────────────────────────────────────────  │
│   Full sandwich visible, validates ingredient memory was correct ✓              │
└─────────────────────────────────────────────────────────────────────────────────┘

★ KEY INNOVATION: Ingredient details maintained despite occlusion
"""
    
    ax.text(0.02, 0.98, preservation_text, fontsize=8, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # Row 4: Volume Integration (J) - Full width
    ax = fig.add_subplot(gs[3, :])
    ax.axis('off')
    
    volume_text = """
(J) VOLUME INTEGRATION ACROSS PARTIAL OCCLUSIONS

┌────────┬───────────┬────────────┬────────────┬────────────┬───────────────────────────────┐
│ Frame  │ Visibility│   Volume   │ Uncertainty│   Weight   │ Strategy                      │
├────────┼───────────┼────────────┼────────────┼────────────┼───────────────────────────────┤
│   2    │   100%    │   320 ml   │    ±12 ml  │   1.00  ★  │ High-quality frame used       │
│   6    │    50%    │   285 ml   │    ±38 ml  │   0.35     │ Tracking only (not volume)    │
│  10    │    25%    │   240 ml   │    ±65 ml  │   0.15     │ Tracking only (not volume)    │
│  14    │   100%    │   318 ml   │    ±14 ml  │   1.00  ★  │ High-quality frame used       │
└────────┴───────────┴────────────┴────────────┴────────────┴───────────────────────────────┘

Aggregation Strategy:
  • High-visibility frames (>80%) weighted heavily for volume calculation
  • Low-visibility frames (<40%) used ONLY for tracking, excluded from volume
  • Final volume from unoccluded frames: (320ml + 318ml) / 2 = 319 ml

Final Sandwich Volume: 319 ml ± 13 ml
Estimated Weight: 275g (sandwich density: ~0.86 g/ml)

Nutritional Analysis: 485 kcal (35g protein, 20g fat, 38g carbs)
  Ingredients: Bread (180 kcal), Turkey (110 kcal), Cheese (140 kcal), Vegetables (15 kcal), Mayo (40 kcal)

Ground Truth Validation: Actual: 280g, 495 kcal | System: 275g, 485 kcal | Error: -2.0% ✓

✓ Occlusion does not prevent accurate measurement when multiple frames available
✓ Ingredient-level nutrition maintained throughout occlusion sequence
"""
    
    ax.text(0.02, 0.98, volume_text, fontsize=7, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    
    # Save
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    print(f"✓ Figure 3 saved: {output_path}")
    print(f"  Resolution: {FIGSIZE[0]*DPI} x {FIGSIZE[1]*DPI} pixels at {DPI} DPI")
    
    plt.close()

if __name__ == "__main__":
    main()
