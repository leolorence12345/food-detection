#!/usr/bin/env python3
"""
Generate Figure 4: Single-Image Embodiment with Ingredient-Aware Nutrition Estimation
Patent Example 4
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
DPI = 300
FIGSIZE = (11, 14)  # 11" x 14" portrait
OUTPUT_FILE = "Figure_4_Single_Image.png"

def create_breakfast_image(width, height, image_type='original'):
    """Create breakfast plate image"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    center_x, center_y = width // 2, height // 2
    
    # Draw plate (large circle)
    plate_radius = 120
    draw.ellipse([center_x-plate_radius, center_y-20, center_x+plate_radius, center_y+220],
                outline='gray', width=3)
    draw.text((center_x-60, center_y+230), "Plate: 25cm", fill='gray', font=small_font)
    
    # Draw eggs (scrambled - irregular yellow shape)
    egg_color = '#FFD700'
    draw.ellipse([center_x-90, center_y+30, center_x-20, center_y+90],
                fill=egg_color, outline='#DAA520', width=2)
    draw.ellipse([center_x-70, center_y+50, center_x-10, center_y+100],
                fill=egg_color, outline='#DAA520', width=2)
    
    # Draw bacon (3 strips - wavy rectangles)
    bacon_color = '#DC143C'
    for i in range(3):
        x_offset = 20 + i * 25
        y_offset = 40 + i * 10
        draw.rectangle([center_x+x_offset, center_y+y_offset, 
                       center_x+x_offset+60, center_y+y_offset+15],
                      fill=bacon_color, outline='#8B0000', width=2)
    
    # Draw toast (2 slices - rounded rectangles)
    toast_color = '#D2691E'
    draw.rounded_rectangle([center_x-80, center_y+120, center_x-20, center_y+190],
                          radius=5, fill=toast_color, outline='#8B4513', width=2)
    draw.rounded_rectangle([center_x-10, center_y+120, center_x+50, center_y+190],
                          radius=5, fill=toast_color, outline='#8B4513', width=2)
    
    # Draw coffee mug (top-left)
    mug_x, mug_y = center_x-140, center_y-80
    draw.ellipse([mug_x, mug_y, mug_x+60, mug_y+80],
                fill='#654321', outline='#3E2723', width=2)
    # Handle
    draw.arc([mug_x+55, mug_y+20, mug_x+80, mug_y+60],
            start=270, end=90, fill='#3E2723', width=3)
    # Coffee surface
    draw.ellipse([mug_x+5, mug_y+10, mug_x+55, mug_y+25],
                fill='#2C1810', outline='#000000', width=1)
    
    # Add type-specific overlays
    if image_type == 'detection':
        # Bounding boxes
        draw.rectangle([center_x-95, center_y+25, center_x-5, center_y+105],
                      outline='red', width=4)
        draw.text((center_x-90, center_y+30), "Eggs #1", fill='red', font=small_font)
        
        draw.rectangle([center_x+15, center_y+35, center_x+110, center_y+90],
                      outline='blue', width=4)
        draw.text((center_x+20, center_y+40), "Bacon #2", fill='blue', font=small_font)
        
        draw.rectangle([center_x-85, center_y+115, center_x+55, center_y+195],
                      outline='green', width=4)
        draw.text((center_x-80, center_y+120), "Toast #3", fill='green', font=small_font)
        
        draw.rectangle([mug_x-5, mug_y-5, mug_x+85, mug_y+85],
                      outline='yellow', width=4)
        draw.text((mug_x, mug_y-20), "Coffee #4", fill='gold', font=small_font)
    
    elif image_type == 'segmentation':
        # Segmentation masks with transparency
        draw.ellipse([center_x-90, center_y+30, center_x-10, center_y+100],
                    fill=(255, 0, 0, 100), outline='red', width=3)
        draw.text((center_x-50, center_y+60), "ID:1", fill='white', font=font,
                 stroke_width=2, stroke_fill='black')
        
        for i in range(3):
            x_offset = 20 + i * 25
            y_offset = 40 + i * 10
            draw.rectangle([center_x+x_offset, center_y+y_offset, 
                           center_x+x_offset+60, center_y+y_offset+15],
                          fill=(0, 0, 255, 100), outline='blue', width=3)
        draw.text((center_x+50, center_y+65), "ID:2", fill='white', font=font,
                 stroke_width=2, stroke_fill='black')
        
        draw.rounded_rectangle([center_x-80, center_y+120, center_x+50, center_y+190],
                              radius=5, fill=(0, 255, 0, 100), outline='green', width=3)
        draw.text((center_x-20, center_y+150), "ID:3", fill='white', font=font,
                 stroke_width=2, stroke_fill='black')
        
        draw.ellipse([mug_x, mug_y, mug_x+60, mug_y+80],
                    fill=(255, 255, 0, 100), outline='yellow', width=3)
        draw.text((mug_x+15, mug_y+35), "ID:4", fill='black', font=font,
                 stroke_width=2, stroke_fill='white')
        
        # Add depth map indicator
        draw.text((10, height-40), "Depth map applied", fill='purple', font=small_font)
    
    # Title
    if image_type == 'original':
        draw.text((10, 10), "Breakfast Plate", fill='black', font=font)
        draw.text((10, 40), "Single Image Input", fill='blue', font=small_font)
    
    return np.array(img)

def main():
    """Generate Figure 4"""
    print("Generating Figure 4: Single-Image Embodiment...")
    
    # Create figure
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    gs = gridspec.GridSpec(5, 3, figure=fig, hspace=0.5, wspace=0.3,
                          top=0.94, bottom=0.05, left=0.05, right=0.95)
    
    # Title
    fig.suptitle('FIGURE 4: Single-Image Analysis with Ingredient-Aware Nutrition Estimation\nPatent Example 4',
                fontsize=16, fontweight='bold')
    
    # Row 1: Input, Detection, Segmentation (A, B, C)
    ax = fig.add_subplot(gs[0, 0])
    img = create_breakfast_image(500, 400, 'original')
    ax.imshow(img)
    ax.set_title('(A) Input Image\nSingle Static Photo', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    ax = fig.add_subplot(gs[0, 1])
    img = create_breakfast_image(500, 400, 'detection')
    ax.imshow(img)
    ax.set_title('(B) Detection\n+ Bounding Boxes', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    ax = fig.add_subplot(gs[0, 2])
    img = create_breakfast_image(500, 400, 'segmentation')
    ax.imshow(img)
    ax.set_title('(C) Segmentation\n+ Depth Map', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    # Row 2: Calibration & Volume (D) - Full width
    ax = fig.add_subplot(gs[1, :])
    ax.axis('off')
    
    calibration_text = """
(D) CALIBRATION & VOLUME CALCULATION

Auto-Calibration:
  • Plate detected: 25cm diameter (standard dinner plate)
  • Plate bounding box: 200px width → Pixels per cm: 200px / 25cm = 8.0 px/cm
  • Reference depth: 0.42 (plate surface from depth map)

┌──────────┬──────────┬─────────┬─────────┬──────────────────────────────────────────┐
│ Food ID  │ Volume   │ Weight  │ Depth   │ Calibration Method                       │
├──────────┼──────────┼─────────┼─────────┼──────────────────────────────────────────┤
│ Eggs #1  │ 95 ml    │ 100g    │0.42-0.48│ Using plate reference (2 eggs detected) │
│ Bacon #2 │ 42 ml    │ 35g     │0.41-0.43│ Using plate reference (3 strips)        │
│ Toast #3 │ 128 ml   │ 62g     │0.41-0.45│ Using plate reference (2 slices)        │
│ Coffee#4 │ 240 ml   │ 240g    │0.38-0.48│ Cup height + liquid level detection     │
└──────────┴──────────┴─────────┴─────────┴──────────────────────────────────────────┘

✓ Single frame provides complete measurement without video
"""
    
    ax.text(0.02, 0.95, calibration_text, fontsize=8, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # Row 3: Ingredient Descriptions (E) - Full width
    ax = fig.add_subplot(gs[2, :])
    ax.axis('off')
    
    ingredients_text = """
(E) INGREDIENT-LEVEL SEMANTIC DESCRIPTIONS (Single Frame)

Object #1: "Scrambled Eggs" (2 eggs)
  Detected Ingredients: Eggs (yellow-pale color, fluffy texture), Butter/oil (glossy surface sheen)
  Visual Cues: Scrambled preparation (irregular shape), Cooked texture, Light yellow color
  Compositional Analysis: 2 large eggs (~100g total), Cooking fat: ~5g

Object #2: "Bacon Strips" (3 strips)
  Detected Ingredients: Pork bacon (pink-red meat with white fat stripes)
  Visual Cues: Crispy texture (edges curled, dark brown), 3 distinct strips visible, Well-done
  Compositional Analysis: 3 strips × ~12g each = ~35g total, High fat content (~40%)

Object #3: "Whole Wheat Toast" (2 slices)
  Detected Ingredients: Whole wheat bread (brown color, grain texture), Butter (melted, glossy)
  Visual Cues: Toasted (golden-brown surface), 2 slices square shape, Butter melted, Grain texture visible
  Compositional Analysis: 2 slices × ~31g = ~62g bread, Butter: ~8g total

Object #4: "Black Coffee" (8 oz mug)
  Detected Ingredients: Brewed coffee (dark brown liquid)
  Visual Cues: Black coffee (no cream), Hot beverage, Mug 85% full, No sugar detected
  Compositional Analysis: 240ml (8 oz × 85% full)

★ All ingredient descriptions generated from SINGLE IMAGE - No manual input required
"""
    
    ax.text(0.02, 0.98, ingredients_text, fontsize=7.5, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # Row 4: Nutrition Results (F) - Full width
    ax = fig.add_subplot(gs[3, :])
    ax.axis('off')
    
    nutrition_text = """
(F) COMPLETE NUTRITIONAL ANALYSIS (Single-Image Embodiment)

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Object #1: Scrambled Eggs (2 large eggs + butter)                                              │
│   Calories: 185 kcal  │  Protein: 12g  │  Fat: 14g  │  Carbs: 1g  │  Cholesterol: 370mg        │
│   Ingredient Breakdown: Eggs (100g): 155 kcal, 12g protein | Butter (5g): 30 kcal, 3g fat     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Object #2: Bacon (3 strips, crispy)                                                            │
│   Calories: 130 kcal  │  Protein: 9g  │  Fat: 10g  │  Carbs: 0g  │  Sodium: 450mg (high)       │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Object #3: Whole Wheat Toast with Butter (2 slices)                                            │
│   Calories: 245 kcal  │  Protein: 7g  │  Fat: 9g  │  Carbs: 34g  │  Fiber: 5g                  │
│   Ingredient Breakdown: Bread (62g): 165 kcal | Butter (8g): 80 kcal, 9g fat                  │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Object #4: Black Coffee (8 oz)                                                                 │
│   Calories: 2 kcal (negligible)  │  Protein: 0g  │  Fat: 0g  │  Caffeine: ~95mg                │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
║ TOTAL BREAKFAST MEAL                                                                          ║
║ ───────────────────────────────────────────────────────────────────────────────────────────── ║
║  Total Calories: 562 kcal  │  Protein: 28g (20%)  │  Fat: 33g (53%)  │  Carbs: 35g (25%)     ║
║  Sodium: 770mg  │  Cholesterol: 400mg  │  Fiber: 5g                                          ║
║                                                                                               ║
║  ★ Complete nutrition analysis from SINGLE IMAGE                                              ║
║  ★ No video required - Works with one frame                                                   ║
║  ★ Ingredient-aware estimation without manual input                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════╝
"""
    
    ax.text(0.02, 0.98, nutrition_text, fontsize=7, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    
    # Row 5: Comparison Table
    ax = fig.add_subplot(gs[4, :])
    ax.axis('off')
    
    comparison_data = [
        ['Feature', 'Single Image', 'Video (15 frames)'],
        ['Processing Time', '30-45 sec', '5-6 min'],
        ['Volume Accuracy', '±18%', '±15%'],
        ['User Convenience', 'Very easy', 'Moderate'],
        ['Cost per Analysis', '$0.005', '$0.01-0.02'],
        ['Best Use Case', 'Static meals', 'Complex scenes'],
    ]
    
    table = ax.table(cellText=comparison_data, cellLoc='center', loc='center',
                    colWidths=[0.3, 0.35, 0.35])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(3):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax.set_title('Single Image vs. Video Comparison', fontsize=11, fontweight='bold', pad=10)
    
    # Ground truth
    ax.text(0.5, -0.12, 'Ground Truth Validation: System: 562 kcal | Actual: 577 kcal | Error: -2.6% ✓',
           ha='center', fontsize=9, style='italic',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5),
           transform=ax.transAxes)
    
    # Save
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    print(f"✓ Figure 4 saved: {output_path}")
    print(f"  Resolution: {FIGSIZE[0]*DPI} x {FIGSIZE[1]*DPI} pixels at {DPI} DPI")
    
    plt.close()

if __name__ == "__main__":
    main()
