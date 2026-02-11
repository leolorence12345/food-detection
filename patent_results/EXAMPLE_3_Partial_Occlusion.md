# FIGURE 3: Handling Partial Occlusion with Ingredient Preservation

## Patent Example 3: Sandwich with Hand/Napkin Occlusion

---

## Figure Layout (3 rows × 4 columns)

```
┌──────────────────────────────────────────────────────────────────┐
│  FIGURE 3: Partial Occlusion Handling with Ingredient Memory     │
├────────────┬────────────┬────────────┬──────────────────────────┤
│ (A) Frame 2│ (B) Frame 6│ (C) Frame 10│ (D) Frame 14            │
│ Unoccluded │ Partial    │ Heavy      │ Unoccluded              │
│ View       │ Occlusion  │ Occlusion  │ View                    │
│            │            │            │                         │
│  🥪       │  🥪  ✋   │  ✋🥪    │  🥪                     │
│ (full)     │ (50%)      │ (25% vis.) │ (full)                  │
└────────────┴────────────┴────────────┴──────────────────────────┘
┌────────────┬────────────┬────────────┬──────────────────────────┐
│ (E) Seg.   │ (F) Seg.   │ (G) Seg.   │ (H) Ingredient           │
│ Frame 2    │ Frame 6    │ Frame 10   │ Tracking Table           │
│            │            │            │                         │
│ Full mask  │ Partial    │ Minimal    │ Frame │ Visibility      │
│ ID: 1      │ mask       │ mask       │   2   │ 100% ✓          │
│ 100% vis.  │ ID: 1      │ ID: 1      │   6   │ 50%  ✓          │
│            │ 50% vis.   │ 25% vis.   │  10   │ 25%  ✓          │
│            │            │            │  14   │ 100% ✓          │
│            │            │            │                         │
│            │            │            │ Same ID maintained      │
└────────────┴────────────┴────────────┴──────────────────────────┘
┌────────────────────────────────────────────────────────────────┐
│ (I) Ingredient-Level Description Preservation                  │
│                                                                 │
│  OBJECT #1: "Turkey & Cheese Sandwich" (ID persists: Frames 0-20)│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Frame 2 (Unoccluded): FULL ingredient detection        │  │
│  │ ────────────────────────────────────────────────────────│  │
│  │  Detected Ingredients:                                  │  │
│  │    • Whole wheat bread (2 slices, top & bottom)         │  │
│  │    • Turkey slices (3-4 layers, visible at edges)       │  │
│  │    • Cheddar cheese (2 slices, yellow-orange color)     │  │
│  │    • Lettuce (green leaves protruding)                  │  │
│  │    • Tomato slices (red, 2 slices visible)              │  │
│  │    • Mayonnaise (white spread visible at edges)         │  │
│  │                                                          │  │
│  │  → STORED in object memory for ID #1                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Frame 6 (50% Occluded by hand): PARTIAL visibility     │  │
│  │ ────────────────────────────────────────────────────────│  │
│  │  Visible:                                               │  │
│  │    • Bread (bottom slice visible)                       │  │
│  │    • Lettuce edge (green showing)                       │  │
│  │                                                          │  │
│  │  Occluded (not visible):                                │  │
│  │    • Turkey (hand covering)                             │  │
│  │    • Cheese (hand covering)                             │  │
│  │    • Top bread slice (hand covering)                    │  │
│  │                                                          │  │
│  │  → RETAINED from Frame 2 (ingredient memory)            │  │
│  │  → Same Object ID #1 confirmed                          │  │
│  │  → Full ingredient list preserved                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Frame 10 (75% Occluded by hand+napkin): MINIMAL vis.   │  │
│  │ ────────────────────────────────────────────────────────│  │
│  │  Visible:                                               │  │
│  │    • Small portion of bread edge                        │  │
│  │                                                          │  │
│  │  Occluded:                                              │  │
│  │    • Nearly entire sandwich hidden                      │  │
│  │                                                          │  │
│  │  → STILL matched to Object ID #1                        │  │
│  │  → All ingredients preserved from Frame 2               │  │
│  │  → No loss of compositional information                 │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Frame 14 (Unoccluded): Hand removed                     │  │
│  │ ────────────────────────────────────────────────────────│  │
│  │  Detected:                                              │  │
│  │    • Full sandwich visible again                        │  │
│  │    • Confirms ingredient list from Frame 2              │  │
│  │                                                          │  │
│  │  → Validates preserved ingredient memory ✓              │  │
│  │  → Same Object ID #1 throughout                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ✓ Ingredient details maintained despite occlusion              │
│  ✓ No re-detection required when hand moves away               │
│  ✓ Nutritional calculation uses complete ingredient list       │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│ (J) Volume Integration Across Partial Occlusions                │
│                                                                  │
│  ┌────────┬───────────┬────────────┬────────────┬────────────┐  │
│  │ Frame  │ Visibility│   Volume   │ Uncertainty│   Weight   │  │
│  │   #    │    (%)    │   (ml)     │   (±ml)    │  Factor    │  │
│  ├────────┼───────────┼────────────┼────────────┼────────────┤  │
│  │   2    │   100%    │   320      │    ±12     │   1.00  ★  │  │
│  │   6    │    50%    │   285      │    ±38     │   0.35     │  │
│  │  10    │    25%    │   240      │    ±65     │   0.15     │  │
│  │  14    │   100%    │   318      │    ±14     │   1.00  ★  │  │
│  └────────┴───────────┴────────────┴────────────┴────────────┘  │
│                                                                  │
│  Aggregation Strategy:                                          │
│    • High-visibility frames (>80%) weighted heavily             │
│    • Low-visibility frames (<40%) used only for tracking        │
│    • Final volume from unoccluded frames: (320+318)/2 = 319ml  │
│                                                                  │
│  Final Sandwich Volume: 319 ml ± 13 ml                          │
│  Estimated Weight: 275g (sandwich density: ~0.86 g/ml)          │
│                                                                  │
│  ✓ Occlusion does not prevent accurate measurement              │
│  ✓ Multiple unoccluded frames provide robust estimate           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Detailed Panel Specifications

### Row 1: Original Video Frames with Occlusion Progression (A-D)

**Scene Description:**
- Turkey & cheese sandwich on plate (25cm diameter)
- Hand enters frame at t=2s, exits at t=5s
- White napkin partially visible in frame 10
- Indoor lighting, overhead camera angle

**Panel A - Frame 2 (Unoccluded)**
```
┌─────────────────────────┐
│                         │
│    Full Sandwich        │
│    ┌──────────┐         │
│    │   🥪     │         │  ← Complete visibility
│    │  ╱▔▔▔╲  │         │  ← Bread visible
│    │ │ 🥬🍅 │ │         │  ← Lettuce, tomato edges
│    │  ╲___╱  │         │  ← Bottom bread
│    └──────────┘         │
│                         │
│ Plate: 25cm (reference) │
│ No occlusion            │
│ Optimal for detection   │
│ and ingredient ID       │
└─────────────────────────┘
```

**Panel B - Frame 6 (50% Occluded)**
```
┌─────────────────────────┐
│         ✋              │  ← Hand entering
│        /│\              │     from right
│       / │ \             │
│      /  │  \            │
│     /   🥪  \           │  ← Sandwich 50%
│    │   ╱▔╲  │          │     hidden by hand
│    │  │🥬│ │           │
│    │   ╲_╱  │          │
│    └────────┘           │
│                         │
│ Hand covers top half    │
│ Bottom portion visible  │
│ Same sandwich (ID=1)    │
└─────────────────────────┘
```

**Panel C - Frame 10 (75% Occluded)**
```
┌─────────────────────────┐
│    ┌────────┐           │
│    │ Napkin │           │  ← White napkin
│    │   ✋   │           │  ← Hand still present
│    │  /│\ ┆🥪          │  ← Only small edge
│    │ / │ \┆│           │     of sandwich
│    │/  │  \│           │     visible
│    └────────┘           │
│                         │
│ 75% occluded            │
│ Heavy occlusion         │
│ Minimal visibility      │
│ But still tracked!      │
└─────────────────────────┘
```

**Panel D - Frame 14 (Unoccluded Again)**
```
┌─────────────────────────┐
│                         │
│    Full Sandwich        │  ← Hand removed
│    ┌──────────┐         │  ← Napkin moved
│    │   🥪     │         │
│    │  ╱▔▔▔╲  │         │  ← Full visibility
│    │ │ 🥬🍅 │ │         │     restored
│    │  ╲___╱  │         │
│    └──────────┘         │
│                         │
│ Occlusion cleared       │
│ Same sandwich (ID=1)    │
│ Confirms ingredient     │
│ preservation worked     │
└─────────────────────────┘
```

---

### Row 2: Segmentation Masks + Ingredient Tracking

**Panel E - Frame 2 Segmentation (Full)**
```
┌───────────────────────────────┐
│  Segmentation Mask:           │
│                               │
│  ┌─────────────────┐          │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓  │          │  ← Green overlay
│  │  ▓ Object #1 ▓  │          │     (100% visible)
│  │  ▓  Sandwich ▓  │          │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓  │          │
│  └─────────────────┘          │
│                               │
│  Mask Quality: EXCELLENT      │
│  Pixel count: 12,450          │
│  Confidence: 0.94             │
│                               │
│  Ingredient Detection:        │
│  ✓ Bread (top & bottom)       │
│  ✓ Turkey layers (visible)    │
│  ✓ Cheese (yellow-orange)     │
│  ✓ Lettuce (green edges)      │
│  ✓ Tomato (red slices)        │
│  ✓ Condiments (white spread)  │
│                               │
│  → Full ingredient list       │
│     saved to Object #1        │
└───────────────────────────────┘
```

**Panel F - Frame 6 Segmentation (50% Occluded)**
```
┌───────────────────────────────┐
│  Segmentation Mask:           │
│                               │
│  ┌─────────────────┐          │
│  │  ░░░░░░░░░░     │          │  ← Gray area: hand
│  │  ░░ HAND ░      │          │     (not segmented)
│  │  ░░░░░░░░░      │          │
│  │  ▓▓▓▓▓▓▓▓▓▓     │          │  ← Green: sandwich
│  │  ▓ Obj #1 ▓     │          │     (partial mask)
│  └─────────────────┘          │
│                               │
│  Mask Quality: PARTIAL        │
│  Pixel count: 6,180 (50%)     │
│  Confidence: 0.72             │
│                               │
│  Visible This Frame:          │
│  ✓ Bottom bread slice         │
│  ✓ Lettuce edge               │
│                               │
│  Preserved from Frame 2:      │
│  ✓ Turkey (occluded now)      │
│  ✓ Cheese (occluded now)      │
│  ✓ Top bread (occluded now)   │
│  ✓ Tomato (occluded now)      │
│                               │
│  → Object ID #1 matched       │
│  → Ingredient memory active   │
└───────────────────────────────┘
```

**Panel G - Frame 10 Segmentation (25% Visible)**
```
┌───────────────────────────────┐
│  Segmentation Mask:           │
│                               │
│  ┌─────────────────┐          │
│  │  ▒▒▒▒▒▒▒▒▒      │          │  ← Napkin (white)
│  │  ▒NAPKIN▒       │          │
│  │  ░░░░░░░░       │          │  ← Hand (gray)
│  │  ░ HAND ░       │          │
│  │  ░░░░░░▓▓       │          │  ← Tiny sandwich
│  │       ▓▓        │          │     visible portion
│  └─────────────────┘          │
│                               │
│  Mask Quality: MINIMAL        │
│  Pixel count: 3,115 (25%)     │
│  Confidence: 0.58             │
│                               │
│  Visible This Frame:          │
│  ✓ Small bread edge only      │
│                               │
│  Still Tracked:               │
│  ✓ Object ID #1 maintained    │
│  ✓ Position tracked           │
│  ✓ All 6 ingredients          │
│     preserved in memory       │
│                               │
│  Volume Measurement:          │
│  ⚠ Low confidence (±65ml)     │
│  → Excluded from final calc   │
└───────────────────────────────┘
```

**Panel H - Ingredient Tracking Table**
```
╔═══════════════════════════════════╗
║ INGREDIENT MEMORY TRACKING        ║
╠═══════════════════════════════════╣
║                                   ║
║ Object #1: "Turkey Sandwich"      ║
║ ──────────────────────────────    ║
║                                   ║
║ Frame │ Visibility│ Ingredient    ║
║   #   │    (%)    │   Status      ║
║ ──────┼───────────┼─────────────  ║
║   2   │   100%    │ ✓ DETECTED   ║
║       │           │   ALL 6       ║
║       │           │ • Bread (×2)  ║
║       │           │ • Turkey      ║
║       │           │ • Cheese      ║
║       │           │ • Lettuce     ║
║       │           │ • Tomato      ║
║       │           │ • Mayo        ║
║       │           │               ║
║       │           │ → STORED      ║
║ ──────┼───────────┼─────────────  ║
║   6   │    50%    │ ✓ PRESERVED  ║
║       │           │   Visible:    ║
║       │           │   • Bread     ║
║       │           │   • Lettuce   ║
║       │           │               ║
║       │           │   Hidden:     ║
║       │           │   • Turkey    ║
║       │           │   • Cheese    ║
║       │           │   • Tomato    ║
║       │           │               ║
║       │           │ → RETAINED    ║
║       │           │   from memory ║
║ ──────┼───────────┼─────────────  ║
║  10   │    25%    │ ✓ PRESERVED  ║
║       │           │   Visible:    ║
║       │           │   • Edge only ║
║       │           │               ║
║       │           │   Hidden:     ║
║       │           │   • All else  ║
║       │           │               ║
║       │           │ → ALL 6 kept  ║
║       │           │   in memory   ║
║ ──────┼───────────┼─────────────  ║
║  14   │   100%    │ ✓ CONFIRMED  ║
║       │           │   Re-detected ║
║       │           │   all 6       ║
║       │           │               ║
║       │           │ → Validates   ║
║       │           │   memory was  ║
║       │           │   correct ✓   ║
║ ──────┴───────────┴─────────────  ║
║                                   ║
║ ★ Key Innovation:                 ║
║   Ingredient details from         ║
║   unoccluded frames are           ║
║   preserved and associated        ║
║   with object even when           ║
║   heavily occluded                ║
║                                   ║
╚═══════════════════════════════════╝
```

---

### Panel I: Ingredient-Level Description Preservation

(See detailed text in the layout above - this panel shows the complete ingredient preservation logic across occlusion states)

---

### Panel J: Volume Integration Strategy

```
╔════════════════════════════════════════════════════════════════╗
║  VOLUME MEASUREMENT WITH OCCLUSION HANDLING                    ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Frame-by-Frame Volume Measurements:                           ║
║  ═══════════════════════════════════════                       ║
║                                                                ║
║  ┌───────┬──────────┬───────┬───────────┬─────────┬────────┐  ║
║  │Frame  │Visibility│Volume │Uncertainty│Depth    │Weight  │  ║
║  │  #    │   (%)    │ (ml)  │  (±ml)    │Quality  │Factor  │  ║
║  ├───────┼──────────┼───────┼───────────┼─────────┼────────┤  ║
║  │  2    │  100%    │ 320   │   ±12     │ HIGH    │ 1.00★  │  ║
║  │       │          │       │           │         │        │  ║
║  │       │ Full sandwich visible from all angles           │  ║
║  │       │ Depth map complete                               │  ║
║  │       │ Confidence: 0.94                                 │  ║
║  ├───────┼──────────┼───────┼───────────┼─────────┼────────┤  ║
║  │  6    │   50%    │ 285   │   ±38     │ MEDIUM  │ 0.35   │  ║
║  │       │          │       │           │         │        │  ║
║  │       │ Hand occludes top half                           │  ║
║  │       │ Depth map incomplete (top missing)               │  ║
║  │       │ Volume underestimated                            │  ║
║  │       │ Confidence: 0.72                                 │  ║
║  │       │ → Used only for tracking, not final volume       │  ║
║  ├───────┼──────────┼───────┼───────────┼─────────┼────────┤  ║
║  │  10   │   25%    │ 240   │   ±65     │ LOW     │ 0.15   │  ║
║  │       │          │       │           │         │        │  ║
║  │       │ Heavy occlusion by hand + napkin                 │  ║
║  │       │ Only small edge visible                          │  ║
║  │       │ Volume severely underestimated                   │  ║
║  │       │ Confidence: 0.58                                 │  ║
║  │       │ → Used only for tracking, excluded from volume   │  ║
║  ├───────┼──────────┼───────┼───────────┼─────────┼────────┤  ║
║  │  14   │  100%    │ 318   │   ±14     │ HIGH    │ 1.00★  │  ║
║  │       │          │       │           │         │        │  ║
║  │       │ Occlusion cleared                                │  ║
║  │       │ Full sandwich visible again                      │  ║
║  │       │ Depth map complete                               │  ║
║  │       │ Confidence: 0.93                                 │  ║
║  └───────┴──────────┴───────┴───────────┴─────────┴────────┘  ║
║                                                                ║
║  Aggregation Strategy:                                         ║
║  ═══════════════════════════════════════                       ║
║                                                                ║
║  Step 1: Filter by visibility threshold                        ║
║    • Include frames with visibility ≥ 80%                      ║
║    • Frames 2 and 14 qualify                                   ║
║    • Frames 6 and 10 excluded (too occluded)                   ║
║                                                                ║
║  Step 2: Weight by confidence                                  ║
║    • Frame 2:  320ml × 0.94 = 300.8                            ║
║    • Frame 14: 318ml × 0.93 = 295.7                            ║
║    • Total: 596.5 / 1.87 = 319.0 ml                            ║
║                                                                ║
║  Step 3: Compute final uncertainty                             ║
║    • σ_combined = √[(12² + 14²) / 2] = ±13 ml                 ║
║                                                                ║
║  Final Result:                                                 ║
║  ═══════════════════════════════════════                       ║
║                                                                ║
║    Volume: 319 ml ± 13 ml                                      ║
║    Weight: 275g (sandwich density: 0.86 g/ml)                  ║
║    Dimensions: 12cm × 11cm × 4cm (estimated)                   ║
║                                                                ║
║  ✓ Occlusion did not prevent accurate measurement              ║
║  ✓ High-quality frames weighted heavily                        ║
║  ✓ Low-quality frames used only for tracking                   ║
║                                                                ║
║  Nutritional Analysis (with preserved ingredients):            ║
║  ═══════════════════════════════════════                       ║
║                                                                ║
║    Total Calories: 485 kcal                                    ║
║                                                                ║
║    Ingredient Breakdown:                                       ║
║      • Bread (2 slices, 70g):     180 kcal, 6g protein        ║
║      • Turkey (90g):               110 kcal, 20g protein       ║
║      • Cheese (2 slices, 40g):    140 kcal, 8g protein        ║
║      • Vegetables (lettuce+tomato): 15 kcal, 1g protein       ║
║      • Mayonnaise (1 tbsp, 15g):   40 kcal, 0g protein        ║
║                                                                ║
║    Total Macros:                                               ║
║      Protein: 35g                                              ║
║      Fat: 20g                                                  ║
║      Carbohydrates: 38g                                        ║
║      Sodium: 1150mg                                            ║
║                                                                ║
║  ★ Full ingredient-level nutrition maintained despite          ║
║    occlusion in intermediate frames                            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## Ground Truth Validation

```
┌────────────────────────────────────────────────────────────┐
│ VALIDATION: Actual Sandwich Measurement                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Ground Truth (disassemble + weigh method):                 │
│   Total weight: 280g                                       │
│   Component weights:                                       │
│     - Bread: 72g                                           │
│     - Turkey: 95g                                          │
│     - Cheese: 42g                                          │
│     - Vegetables: 55g                                      │
│     - Condiments: 16g                                      │
│   Actual calories: 495 kcal                                │
│                                                            │
│ System Output:                                             │
│   Estimated weight: 275g                                   │
│   Estimated calories: 485 kcal                             │
│                                                            │
│ Accuracy:                                                  │
│   Weight error: -1.8% (5g underestimate)                   │
│   Calorie error: -2.0% (10 kcal underestimate)             │
│                                                            │
│ Key Success:                                               │
│   ✓ All 6 ingredients correctly identified                 │
│   ✓ Ingredients preserved through occlusion                │
│   ✓ Volume from unoccluded frames only                     │
│   ✓ High accuracy despite 75% occlusion in some frames     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Key Patent Claims Demonstrated

1. ✓ **Partial occlusion handling** - Object tracked despite 75% occlusion
2. ✓ **Ingredient preservation** - Semantic descriptions retained across frames
3. ✓ **Associating detections** - Occluded frames linked to unoccluded frames
4. ✓ **Persistent identifiers** - Object ID #1 maintained throughout
5. ✓ **Selective volume integration** - Only high-quality frames used for measurement
6. ✓ **Ingredient memory** - Details from Frame 2 used for all subsequent frames
7. ✓ **Robust tracking** - Works even with minimal visibility (25%)
8. ✓ **No information loss** - Full nutritional analysis despite occlusion

---

## Figure Generation Instructions

**Format:** Multi-panel composite figure
**Resolution:** 300 DPI
**Dimensions:** 10" × 12" (portrait orientation)

**Visual Elements:**
- Occlusion indicators: Semi-transparent gray overlay for hand/napkin
- Segmentation masks: Green (#00FF00) for sandwich, 60% opacity
- Tracking lines: Dotted white lines connecting same object across frames
- Ingredient icons: Small visual indicators for each detected ingredient

**Annotations:**
- Visibility percentages: Large bold numbers (e.g., "100%", "50%", "25%")
- Object ID labels: White text in boxes (e.g., "ID: 1")
- Occlusion warnings: Yellow triangles with "⚠" symbol for frames 6 and 10

