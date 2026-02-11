# FIGURE 1: Multi-Food Meal with Ingredient-Level Semantic Description

## Patent Example 1: Video-Based Multi-Food Meal Analysis

---

## Figure Layout (Multi-Panel: 3 rows × 3 columns)

```
┌─────────────────────────────────────────────────────────────────┐
│  FIGURE 1: Multi-Food Meal with Ingredient-Level Description    │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   (A) Frame 1   │   (B) Frame 8   │   (C) Frame 15              │
│   Original      │   Original      │   Original                  │
│   Input Video   │   Input Video   │   Input Video               │
│   [0:00]        │   [0:03]        │   [0:05]                    │
└─────────────────┴─────────────────┴─────────────────────────────┘
┌─────────────────┬─────────────────┬─────────────────────────────┐
│ (D) Detection   │ (E) Detection   │ (F) Detection               │
│  + Bounding Box │  + Bounding Box │  + Bounding Box             │
│  Frame 1        │  Frame 8        │  Frame 15                   │
│  [4 objects]    │  [4 objects]    │  [4 objects]                │
└─────────────────┴─────────────────┴─────────────────────────────┘
┌─────────────────┬─────────────────┬─────────────────────────────┐
│ (G) Segmentation│ (H) Segmentation│ (I) Segmentation            │
│  + Tracking IDs │  + Tracking IDs │  + Tracking IDs             │
│  + Depth Overlay│  + Depth Overlay│  + Depth Overlay            │
└─────────────────┴─────────────────┴─────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│ (J) Ingredient-Level Semantic Descriptions                      │
│                                                                  │
│  Object #1: "Cheeseburger"                                      │
│    → Ingredients: beef patty, cheddar cheese, sesame bun,       │
│      lettuce, tomato, onion                                     │
│    → Visual Cues: melted cheese visible, toasted bun,           │
│      layered structure                                          │
│                                                                  │
│  Object #2: "French Fries"                                      │
│    → Ingredients: potato strips, vegetable oil, salt            │
│    → Visual Cues: golden-brown color, crispy texture,           │
│      stick shape                                                │
│                                                                  │
│  Object #3: "Soft Drink (Cola)"                                 │
│    → Ingredients: carbonated water, sugar, flavoring            │
│    → Visual Cues: dark liquid in glass, ice cubes visible       │
│                                                                  │
│  Object #4: "Garden Salad"                                      │
│    → Ingredients: lettuce, tomato, cucumber, carrot             │
│    → Visual Cues: mixed greens, chopped vegetables, bowl        │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│ (K) Volumetric Measurements & Nutritional Results               │
│                                                                  │
│  ┌────────────┬──────────┬─────────┬──────────┬──────────────┐ │
│  │ Food Item  │ Volume   │ Calories│ Protein  │ Key Feature  │ │
│  │            │ (ml/g)   │ (kcal)  │ (g)      │              │ │
│  ├────────────┼──────────┼─────────┼──────────┼──────────────┤ │
│  │ Burger     │ 280ml    │ 540     │ 28g      │ Composite    │ │
│  │ (Object #1)│ (235g)   │         │          │ ingredients  │ │
│  ├────────────┼──────────┼─────────┼──────────┼──────────────┤ │
│  │ Fries      │ 180ml    │ 365     │ 4g       │ Aggregated   │ │
│  │ (Object #2)│ (145g)   │         │          │ from 15      │ │
│  │            │          │         │          │ frames       │ │
│  ├────────────┼──────────┼─────────┼──────────┼──────────────┤ │
│  │ Soft Drink │ 350ml    │ 140     │ 0g       │ Liquid depth │ │
│  │ (Object #3)│          │         │          │ measurement  │ │
│  ├────────────┼──────────┼─────────┼──────────┼──────────────┤ │
│  │ Salad      │ 220ml    │ 85      │ 3g       │ Mixed        │ │
│  │ (Object #4)│ (165g)   │         │          │ ingredients  │ │
│  ├────────────┼──────────┼─────────┼──────────┼──────────────┤ │
│  │ TOTAL MEAL │ 1030ml   │ 1130    │ 35g      │ No duplicate │ │
│  │            │          │         │          │ counting     │ │
│  └────────────┴──────────┴─────────┴──────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Panel Specifications

### Row 1: Original Video Frames (A, B, C)

**Panel A - Frame 1 (t=0:00)**
- Shows: Restaurant meal on table with all 4 items visible
- Camera angle: 45° overhead view
- Plate (25cm diameter) visible - used for calibration
- All objects clearly visible, no occlusion
- Lighting: Standard indoor restaurant lighting

**Panel B - Frame 8 (t=0:03)**
- Shows: Slight camera movement, same meal
- Camera angle: Slightly rotated (~10° clockwise)
- All 4 items still in frame
- Demonstrates: Same objects maintained across frames

**Panel C - Frame 15 (t=0:05)**
- Shows: End of video sequence
- Camera angle: Returned to similar position as Frame 1
- All 4 items present
- Demonstrates: Consistent detection throughout video

---

### Row 2: Detection + Bounding Boxes (D, E, F)

**Visual Elements:**
- Bounding boxes in different colors:
  - Object #1 (Burger): RED box
  - Object #2 (Fries): GREEN box
  - Object #3 (Drink): BLUE box
  - Object #4 (Salad): YELLOW box
- Each box labeled with: "Object #[ID]: [Food Name]"
- Florence-2 detection confidence scores (e.g., 0.92)

**Panel D - Frame 1 Detection**
```
┌─────────────────────────────────┐
│                                 │
│     [RED: Burger #1: 0.94]     │
│     ┌──────────┐                │
│     │   🍔    │                 │
│     └──────────┘                │
│                                 │
│  [GREEN: Fries #2: 0.89]       │
│  ┌────────┐   [BLUE: Drink #3] │
│  │  🍟   │    ┌──────┐         │
│  └────────┘    │  🥤 │         │
│                └──────┘         │
│  [YELLOW: Salad #4: 0.87]      │
│  ┌────────────┐                │
│  │    🥗     │                 │
│  └────────────┘                │
│                                 │
│ Plate detected: 25cm diameter   │
│ Calibration: 8.0 px/cm         │
└─────────────────────────────────┘
```

**Panels E & F:** Same 4 objects with consistent IDs, slightly different positions

---

### Row 3: Segmentation + Depth (G, H, I)

**Visual Elements:**
- Precise segmentation masks (colored by object ID)
- Depth overlay (heatmap: dark blue = near, red = far)
- Object IDs labeled with arrows
- Tracking consistency indicators

**Panel G - Frame 1 Segmentation**
```
Segmentation Masks (colored regions):
- Burger: Precise outline of bun, visible layers
- Fries: Individual fries segmented as group
- Drink: Glass outline + liquid surface
- Salad: Bowl outline + vegetable pieces

Depth Map Overlay (colormap):
- Plate surface: Medium depth (reference plane)
- Burger: Raised above plate (lighter color)
- Drink: Tall object (gradient from base to top)
- Salad: Bowl depth visible

Annotations:
"ID #1 → #1 → #1" (consistency across frames)
"Volume aggregated: 15 frames"
```

---

### Panel J: Ingredient-Level Semantic Descriptions

**Format:** Structured text with visual cue annotations

```
══════════════════════════════════════════════════════════════
INGREDIENT-LEVEL SEMANTIC DESCRIPTIONS (Generated from Visual Cues)
══════════════════════════════════════════════════════════════

Object #1: "Cheeseburger" (Composite Food)
─────────────────────────────────────────────────────────────
  Detected Ingredients:
    • Beef patty (visual: brown, grilled texture, ~150g)
    • Cheddar cheese (visual: yellow-orange, melted, draped over patty)
    • Sesame seed bun (visual: golden, toasted, seeds visible on top)
    • Lettuce (visual: green leaf, visible at edge)
    • Tomato slice (visual: red, circular, ~5mm thick)
    • Onion (visual: white rings, thin slices)
    
  Preparation Characteristics:
    • Grilled patty (char marks visible)
    • Toasted bun (golden-brown surface)
    • Assembled as layered structure
    
  Compositional Analysis:
    • Bun: ~35% by volume
    • Patty: ~45% by volume
    • Cheese + vegetables: ~20% by volume

─────────────────────────────────────────────────────────────

Object #2: "French Fries" (Uniform Food)
─────────────────────────────────────────────────────────────
  Detected Ingredients:
    • Potato (visual: yellow-golden interior)
    • Vegetable oil (visual: glossy surface sheen)
    • Salt seasoning (visual: white crystals on surface)
    
  Preparation Characteristics:
    • Deep-fried (golden-brown color, crispy appearance)
    • Cut into uniform sticks (~8mm × 8mm × 60mm)
    
  Observable Features:
    • Count: ~35 individual fries
    • Color uniformity: Consistent golden color
    • Texture: Crispy exterior (light reflection indicates oil)

─────────────────────────────────────────────────────────────

Object #3: "Soft Drink - Cola Type" (Beverage)
─────────────────────────────────────────────────────────────
  Detected Ingredients:
    • Carbonated water (visual: bubbles visible at surface)
    • Sugar/sweetener (inferred from cola appearance)
    • Caramel coloring (visual: dark brown liquid)
    • Ice cubes (visual: transparent cubes, ~4 visible)
    
  Observable Features:
    • Liquid level: 85% full (297ml of 350ml glass)
    • Carbonation: Active bubbles at liquid surface
    • Temperature: Cold (condensation on glass exterior)

─────────────────────────────────────────────────────────────

Object #4: "Garden Salad" (Mixed Food)
─────────────────────────────────────────────────────────────
  Detected Ingredients:
    • Lettuce - romaine type (visual: elongated green leaves, ~50%)
    • Tomato (visual: red chunks, diced, ~20%)
    • Cucumber (visual: green slices with seeds, ~15%)
    • Carrot (visual: orange shredded pieces, ~15%)
    
  Preparation Characteristics:
    • Fresh-cut vegetables (crisp appearance)
    • No dressing visible (dry salad)
    • Mixed composition in bowl
    
  Compositional Analysis:
    • Leafy greens: 110ml (~50%)
    • Solid vegetables: 110ml (~50%)
    • Estimated weight: 165g total

══════════════════════════════════════════════════════════════
KEY INNOVATION: Ingredient-level descriptions generated WITHOUT
manual annotation - derived purely from visual analysis
══════════════════════════════════════════════════════════════
```

---

### Panel K: Volumetric Measurements & Nutritional Results

**Table Format with Detailed Breakdown**

```
╔════════════════════════════════════════════════════════════════════════╗
║  VOLUMETRIC MEASUREMENTS AND NUTRITIONAL ANALYSIS RESULTS              ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │ OBJECT #1: CHEESEBURGER (Composite Food)                         │ ║
║  ├──────────────────────────────────────────────────────────────────┤ ║
║  │ Volumetric Measurements:                                         │ ║
║  │   • Total volume: 280 ml                                         │ ║
║  │   • Estimated weight: 235g (density: 0.84 g/ml)                  │ ║
║  │   • Dimensions: 12cm (W) × 10cm (D) × 6cm (H)                    │ ║
║  │   • Frames used: 15/15 (100% visibility)                         │ ║
║  │                                                                   │ ║
║  │ Nutritional Values (Ingredient-Based Calculation):               │ ║
║  │   • Total Calories: 540 kcal                                     │ ║
║  │   • Protein: 28g (21% by weight)                                 │ ║
║  │   • Fat: 28g (24% by weight)                                     │ ║
║  │   • Carbohydrates: 42g (36% by weight)                           │ ║
║  │   • Sodium: 980mg                                                │ ║
║  │                                                                   │ ║
║  │ Ingredient Breakdown (from semantic description):                │ ║
║  │   - Beef patty (150g): 280 kcal, 20g protein, 22g fat           │ ║
║  │   - Bun (70g): 180 kcal, 6g protein, 2g fat, 35g carbs          │ ║
║  │   - Cheese (20g): 65 kcal, 4g protein, 5g fat                   │ ║
║  │   - Vegetables (15g): 15 kcal, 1g protein, 7g carbs             │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │ OBJECT #2: FRENCH FRIES                                          │ ║
║  ├──────────────────────────────────────────────────────────────────┤ ║
║  │ Volumetric Measurements:                                         │ ║
║  │   • Total volume: 180 ml                                         │ ║
║  │   • Estimated weight: 145g (potato density: 0.81 g/ml)           │ ║
║  │   • Count: ~35 individual fries                                  │ ║
║  │   • Multi-frame aggregation: Frames 1-15                         │ ║
║  │                                                                   │ ║
║  │ Nutritional Values:                                              │ ║
║  │   • Total Calories: 365 kcal                                     │ ║
║  │   • Protein: 4g                                                  │ ║
║  │   • Fat: 17g (deep-fried in oil)                                 │ ║
║  │   • Carbohydrates: 48g                                           │ ║
║  │   • Sodium: 280mg                                                │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │ OBJECT #3: SOFT DRINK (COLA)                                     │ ║
║  ├──────────────────────────────────────────────────────────────────┤ ║
║  │ Volumetric Measurements:                                         │ ║
║  │   • Liquid volume: 297 ml (85% of 350ml glass)                   │ ║
║  │   • Ice volume: 53 ml (4 cubes)                                  │ ║
║  │   • Total liquid consumed: 350 ml equivalent                     │ ║
║  │   • Depth-based liquid surface detection                         │ ║
║  │                                                                   │ ║
║  │ Nutritional Values (per 350ml):                                  │ ║
║  │   • Total Calories: 140 kcal                                     │ ║
║  │   • Protein: 0g                                                  │ ║
║  │   • Fat: 0g                                                      │ ║
║  │   • Carbohydrates: 39g (all sugars)                              │ ║
║  │   • Sodium: 45mg                                                 │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │ OBJECT #4: GARDEN SALAD                                          │ ║
║  ├──────────────────────────────────────────────────────────────────┤ ║
║  │ Volumetric Measurements:                                         │ ║
║  │   • Total volume: 220 ml                                         │ ║
║  │   • Estimated weight: 165g (avg density: 0.75 g/ml)              │ ║
║  │   • Bowl depth: 5cm, fill level: 70%                             │ ║
║  │                                                                   │ ║
║  │ Nutritional Values (Multi-Ingredient):                           │ ║
║  │   • Total Calories: 85 kcal                                      │ ║
║  │   • Protein: 3g                                                  │ ║
║  │   • Fat: 0.5g                                                    │ ║
║  │   • Carbohydrates: 18g                                           │ ║
║  │   • Fiber: 6g                                                    │ ║
║  │   • Vitamin A: 350% DV (from carrots)                            │ ║
║  │   • Vitamin C: 45% DV (from tomato, cucumber)                    │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  ╔══════════════════════════════════════════════════════════════════╗ ║
║  ║ COMPLETE MEAL TOTALS                                             ║ ║
║  ╠══════════════════════════════════════════════════════════════════╣ ║
║  ║  Total Volume: 1,030 ml (977g estimated weight)                  ║ ║
║  ║                                                                  ║ ║
║  ║  Total Calories: 1,130 kcal                                      ║ ║
║  ║  Total Protein: 35g  (12% of calories)                           ║ ║
║  ║  Total Fat: 45.5g    (36% of calories)                           ║ ║
║  ║  Total Carbohydrates: 147g (52% of calories)                     ║ ║
║  ║  Total Sodium: 1,305 mg                                          ║ ║
║  ║                                                                  ║ ║
║  ║  ✓ No duplicate counting (same object tracked across 15 frames)  ║ ║
║  ║  ✓ Ingredient-level refinement applied                           ║ ║
║  ║  ✓ Automatic calibration using plate (25cm detected)             ║ ║
║  ╚══════════════════════════════════════════════════════════════════╝ ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## Ground Truth Comparison

```
┌────────────────────────────────────────────────────────────┐
│ VALIDATION AGAINST MANUAL MEASUREMENT                      │
├────────────────┬──────────────┬──────────────┬─────────────┤
│ Food Item      │ System Value │ Ground Truth │ Error %     │
├────────────────┼──────────────┼──────────────┼─────────────┤
│ Burger         │ 540 kcal     │ 530 kcal     │ +1.9%       │
│ Fries          │ 365 kcal     │ 380 kcal     │ -3.9%       │
│ Drink          │ 140 kcal     │ 140 kcal     │ 0.0%        │
│ Salad          │ 85 kcal      │ 90 kcal      │ -5.6%       │
├────────────────┼──────────────┼──────────────┼─────────────┤
│ TOTAL MEAL     │ 1,130 kcal   │ 1,140 kcal   │ -0.9%       │
└────────────────┴──────────────┴──────────────┴─────────────┘

Average Error: ±2.9%
Demonstrates: High accuracy with ingredient-level descriptions
```

---

## Key Patent Claims Demonstrated

1. ✓ **Multi-food scene handling** - 4 distinct food items processed simultaneously
2. ✓ **Ingredient-level semantic descriptions** - Composite foods broken down to ingredients
3. ✓ **Temporal tracking** - Same objects tracked across 15 frames
4. ✓ **No duplicate counting** - Each physical item counted once despite multiple detections
5. ✓ **Automatic calibration** - Plate detected and used for spatial scaling
6. ✓ **Volume aggregation** - Measurements from multiple frames combined
7. ✓ **Depth-based measurements** - 3D volume estimation from 2D video

---

## Figure Generation Instructions

**File Format:** High-resolution PNG or TIFF (300 DPI minimum)
**Dimensions:** 8.5" × 11" (full page) or 7" × 9" (3/4 page)
**Color Scheme:** 
  - Detection boxes: RGB bright colors with 80% opacity
  - Segmentation masks: Solid colors with 60% opacity
  - Depth maps: Jet colormap (blue to red)
  - Text: Black on white background, Arial or Helvetica, 10-12pt

**Software Recommendations:**
- Python: matplotlib, opencv, PIL
- Vector graphics: Adobe Illustrator, Inkscape
- Layout: LaTeX with subfigure package

