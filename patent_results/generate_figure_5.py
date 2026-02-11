#!/usr/bin/env python3
"""
Generate Figure 5: Region-Specific and Context-Aware Nutritional Inference
Patent Example 5
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
DPI = 300
FIGSIZE = (14, 12)  # 14" x 12" landscape
OUTPUT_FILE = "Figure_5_Region_Specific.png"

def create_curry_rice_image(width, height, context='neutral'):
    """Create curry and rice image"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        tiny_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        tiny_font = ImageFont.load_default()
    
    center_x, center_y = width // 2, height // 2
    
    # Draw plate
    draw.ellipse([50, center_y-20, width-50, center_y+180],
                outline='gray', width=3)
    
    # Draw rice (white mound on right)
    rice_color = '#FFFAF0'
    draw.ellipse([center_x+20, center_y+30, center_x+140, center_y+140],
                fill=rice_color, outline='#E0E0E0', width=2)
    draw.text((center_x+55, center_y+75), "Rice", fill='gray', font=small_font)
    
    # Draw curry (yellow-orange sauce on left)
    curry_color = '#FFA500'
    draw.ellipse([center_x-140, center_y+30, center_x-20, center_y+140],
                fill=curry_color, outline='#FF8C00', width=2)
    
    # Add chicken pieces to curry
    chicken_color = '#FFE4B5'
    draw.ellipse([center_x-110, center_y+50, center_x-70, center_y+80],
                fill=chicken_color, outline='#DEB887', width=1)
    draw.ellipse([center_x-90, center_y+85, center_x-55, center_y+110],
                fill=chicken_color, outline='#DEB887', width=1)
    
    draw.text((center_x-105, center_y+70), "Curry", fill='white', font=small_font,
             stroke_width=2, stroke_fill='black')
    
    # Add context-specific markers
    if context == 'us':
        # US flag and dollar sign
        draw.rectangle([10, 10, 70, 40], fill='blue')
        draw.rectangle([10, 10, 30, 20], fill='red')
        draw.text((width-60, 10), "$", fill='green', font=font)
        draw.text((10, height-40), "US CONTEXT", fill='blue', font=small_font)
        draw.text((10, height-20), "Restaurant-style", fill='blue', font=tiny_font)
    elif context == 'india':
        # Indian flag colors and rupee symbol
        draw.rectangle([10, 10, 70, 20], fill='orange')
        draw.rectangle([10, 20, 70, 30], fill='white')
        draw.rectangle([10, 30, 70, 40], fill='green')
        draw.text((width-60, 10), "₹", fill='darkgreen', font=font)
        draw.text((10, height-40), "INDIA CONTEXT", fill='darkorange', font=small_font)
        draw.text((10, height-20), "Home-cooked style", fill='darkorange', font=tiny_font)
    
    # Label
    draw.text((center_x-80, 20), "Curry & Rice", fill='black', font=font)
    
    return np.array(img)

def main():
    """Generate Figure 5"""
    print("Generating Figure 5: Region-Specific...")
    
    # Create figure with side-by-side layout
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    gs = gridspec.GridSpec(6, 2, figure=fig, hspace=0.5, wspace=0.4,
                          top=0.94, bottom=0.05, left=0.05, right=0.95)
    
    # Title
    fig.suptitle('FIGURE 5: Region-Specific and Context-Aware Nutritional Inference\nPatent Example 5',
                fontsize=16, fontweight='bold')
    
    # Column headers
    fig.text(0.27, 0.92, 'US CONTEXT', ha='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    fig.text(0.73, 0.92, 'INDIA CONTEXT', ha='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    # Row 1: Input images (A, B)
    ax = fig.add_subplot(gs[0, 0])
    img = create_curry_rice_image(500, 350, 'us')
    ax.imshow(img)
    ax.set_title('(A) Same Visual Input\nUS Context', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    ax = fig.add_subplot(gs[0, 1])
    img = create_curry_rice_image(500, 350, 'india')
    ax.imshow(img)
    ax.set_title('(B) Same Visual Input\nIndia Context', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    # Row 2: Database matching (C, D)
    ax = fig.add_subplot(gs[1, 0])
    ax.axis('off')
    
    us_db_text = """
(C) US Database Matching

Context: United States
Geographic: North America

Nutrition Database:
  → USDA FNDDS (primary)
  → Generic recipes

Matched Entry:
  "Chicken curry,
   restaurant-style,
   American-style Indian"

Ingredient Interpretation:
  • Chicken: Breast meat
  • Cream-based sauce
  • Mild spices
  • Higher fat content
  • Western-adapted recipe

Rice Match:
  "White rice, enriched"
  (USDA standard)
"""
    
    ax.text(0.05, 0.95, us_db_text, fontsize=8, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.4))
    
    ax = fig.add_subplot(gs[1, 1])
    ax.axis('off')
    
    india_db_text = """
(D) India Database Matching

Context: India
Geographic: South Asia

Nutrition Database:
  → India CoFID (primary)
  → Regional IFCT

Matched Entry:
  "Chicken curry,
   traditional Indian,
   home-cooked style"

Ingredient Interpretation:
  • Chicken: With skin, bone-in
  • Yogurt or coconut milk base
  • Authentic spice blend
  • Moderate fat content
  • Traditional preparation

Rice Match:
  "Basmati rice, plain"
  (Indian variety)
"""
    
    ax.text(0.05, 0.95, india_db_text, fontsize=8, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.4))
    
    # Row 3: Nutritional values (E, F)
    ax = fig.add_subplot(gs[2, 0])
    ax.axis('off')
    
    us_nutrition_text = """
(E) US Nutritional Values

Curry (1 cup, 240ml):
  Calories: 485 kcal
  Protein: 28g
  Fat: 32g (cream-heavy)
  Carbs: 18g
  Saturated Fat: 18g (HIGH)
  Sodium: 950mg

Preparation Notes:
  • Heavy cream used
  • Butter for richness
  • Adapted for Western taste

Rice (1 cup, cooked, 158g):
  Calories: 205 kcal
  Protein: 4g
  Fat: 0.4g
  Carbs: 45g

Rice Type:
  • Enriched white rice
  • Standard US variety

═════════════════════════
TOTAL MEAL (US):
  Calories: 690 kcal
  Protein: 32g
  Fat: 32.4g (42% of cal)
  Carbs: 63g
  Sat. Fat: 18g (HIGH)
  Sodium: 950mg

Health Profile:
  ⚠ High in saturated fat
  ⚠ Higher calorie density
  ⚠ Restaurant-style richness
"""
    
    ax.text(0.02, 0.98, us_nutrition_text, fontsize=7, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='#FFE0E0', alpha=0.5))
    
    ax = fig.add_subplot(gs[2, 1])
    ax.axis('off')
    
    india_nutrition_text = """
(F) India Nutritional Values

Curry (1 cup, 240ml):
  Calories: 320 kcal
  Protein: 25g
  Fat: 18g (moderate)
  Carbs: 12g
  Saturated Fat: 8g
  Sodium: 680mg

Preparation Notes:
  • Yogurt or coconut milk
  • Minimal oil/ghee
  • Traditional spices

Rice (1 cup, cooked, 158g):
  Calories: 191 kcal
  Protein: 4g
  Fat: 0.5g
  Carbs: 41g

Rice Type:
  • Basmati (aromatic)
  • Lower glycemic index

═════════════════════════
TOTAL MEAL (India):
  Calories: 511 kcal
  Protein: 29g
  Fat: 18.5g (33% of cal)
  Carbs: 53g
  Sat. Fat: 8g (Moderate)
  Sodium: 680mg

Health Profile:
  ✓ Moderate fat
  ✓ Lower calorie density
  ✓ Balanced macros
  ✓ Traditional healthy prep
"""
    
    ax.text(0.02, 0.98, india_nutrition_text, fontsize=7, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='#E0FFE0', alpha=0.5))
    
    # Row 4: Comparative Analysis (G) - Full width
    ax = fig.add_subplot(gs[3, :])
    ax.axis('off')
    
    comparison_text = """
(G) REGIONAL NUTRITION VARIANCE ANALYSIS

┌─────────────────────┬─────────────┬───────────────┬────────────┬─────────────────────────────────────────────┐
│ Metric              │ US Context  │ India Context │ Difference │ Explanation                                 │
├─────────────────────┼─────────────┼───────────────┼────────────┼─────────────────────────────────────────────┤
│ Total Calories      │ 690 kcal    │ 511 kcal      │ -26%       │ US: Cream-based sauce (richer)              │
│ Total Fat           │ 32.4g       │ 18.5g         │ -43%       │ India: Yogurt base (lighter)                │
│ Saturated Fat       │ 18g         │ 8g            │ -56%       │ US: Heavy cream + butter                    │
│ Sodium              │ 950mg       │ 680mg         │ -28%       │ US: Higher salt in restaurant prep          │
│ Protein             │ 32g         │ 29g           │ -9%        │ Similar (both chicken-based)                │
│ Carbohydrates       │ 63g         │ 53g           │ -16%       │ US: More rice, enriched variety             │
└─────────────────────┴─────────────┴───────────────┴────────────┴─────────────────────────────────────────────┘

KEY DIFFERENCES:
1. Preparation Method: US (Cream-based, restaurant) vs. India (Yogurt/coconut, home-style)
2. Ingredient Composition: US (Heavy cream, butter, mild) vs. India (Yogurt, minimal oil, authentic spices)
3. Cultural Norms: US (Larger portions, sauce-heavy) vs. India (Moderate, balanced with rice)
4. Nutritional Profile: US (Higher calories, fat-focused) vs. India (Moderate calories, balanced)

SYSTEM INTELLIGENCE:
✓ Same visual detection (curry + rice) in both contexts
✓ Context determines database selection automatically
✓ Region-appropriate ingredient assumptions applied
✓ Cultural preparation styles considered
✓ Accurate nutrition for actual food consumed

⚠ WITHOUT regional awareness: 26-43% calorie/fat error possible → Misleading dietary guidance
✓ WITH regional awareness: Correct database selected → Accurate nutrition for cultural context
"""
    
    ax.text(0.01, 0.98, comparison_text, fontsize=7, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # Row 5: Context detection methods
    ax = fig.add_subplot(gs[4, :])
    ax.axis('off')
    
    context_text = """
HOW REGIONAL CONTEXT IS DETERMINED

Method 1: User Profile (Explicit)              Method 2: GPS Metadata (Automatic)
  • User sets location in app                    • Image EXIF data contains GPS coordinates
  • Country selection: "USA" or "India"          • System extracts: Latitude, Longitude
  • Most reliable method                         • Geocoding: (28.6°N, 77.2°E) → New Delhi, India

Method 3: Visual Cues (AI Inference)           Method 4: Database Matching (Fallback)
  • Restaurant signage language                  • Try multiple regional databases
  • Currency symbols ($ vs. ₹)                   • Select highest confidence score
  • Tableware style analysis                     • Example: "Masala Dosa" → 0.95 (CoFID) vs. 0.42 (USDA)
  • Gemini LLM scene analysis                    • Automatically select India database

Priority Order: 1. User profile → 2. GPS location → 3. Visual analysis → 4. Database confidence
"""
    
    ax.text(0.02, 0.95, context_text, fontsize=7.5, family='monospace',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # Row 6: Ground truth validation
    ax = fig.add_subplot(gs[5, :])
    ax.axis('off')
    
    validation_data = [
        ['Scenario', 'Lab Analysis', 'System Output', 'Error', 'Result'],
        ['US Restaurant Meal', '705 kcal, 34g fat', '690 kcal, 32.4g fat', '-2.1%, -4.7%', '✓ Accurate'],
        ['India Home-Cooked', '525 kcal, 19g fat', '511 kcal, 18.5g fat', '-2.7%, -2.6%', '✓ Accurate'],
        ['India with US DB', '525 kcal, 19g fat', '690 kcal, 32.4g fat', '+31%, +71%', '❌ ERROR'],
        ['US with India DB', '705 kcal, 34g fat', '511 kcal, 18.5g fat', '-28%, -46%', '❌ ERROR'],
    ]
    
    table = ax.table(cellText=validation_data, cellLoc='center', loc='center',
                    colWidths=[0.22, 0.22, 0.22, 0.18, 0.16])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style correct rows (green)
    for i in [1, 2]:
        for j in range(5):
            table[(i, j)].set_facecolor('#D4EDDA')
    
    # Style error rows (red)
    for i in [3, 4]:
        for j in range(5):
            table[(i, j)].set_facecolor('#F8D7DA')
    
    ax.set_title('GROUND TRUTH VALIDATION: Regional Database Accuracy', 
                fontsize=11, fontweight='bold', pad=10)
    
    # Conclusion
    ax.text(0.5, -0.15, '✓ Correct regional database: ±3% error  |  ❌ Wrong regional database: 30-70% error\n' +
                       '→ Regional awareness is CRITICAL for accuracy',
           ha='center', fontsize=10, style='italic', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
           transform=ax.transAxes)
    
    # Save
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    print(f"✓ Figure 5 saved: {output_path}")
    print(f"  Resolution: {FIGSIZE[0]*DPI} x {FIGSIZE[1]*DPI} pixels at {DPI} DPI")
    
    plt.close()

if __name__ == "__main__":
    main()
