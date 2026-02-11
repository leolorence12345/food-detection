# 🚀 Generate Patent Figures

## Quick Start

### 1. Install Dependencies

```bash
cd patent_results
pip install -r requirements.txt
```

### 2. Generate All Figures

```bash
python generate_all_figures.py
```

This will create all 5 figures:
- `Figure_1_Multi_Food_Meal.png`
- `Figure_2_Temporal_Tracking.png`
- `Figure_3_Partial_Occlusion.png`
- `Figure_4_Single_Image.png`
- `Figure_5_Region_Specific.png`

### 3. Generate Individual Figures

You can also generate figures one at a time:

```bash
python generate_figure_1.py
python generate_figure_2.py
python generate_figure_3.py
python generate_figure_4.py
python generate_figure_5.py
```

## Output

- **Resolution**: 300 DPI (patent-quality)
- **Format**: PNG (easily convertible to TIFF)
- **Location**: Same folder as scripts

## Troubleshooting

If you get font warnings, the scripts will use default fonts automatically.

## Next Steps

1. Review generated figures
2. Verify all data matches your system
3. Convert to TIFF if required by USPTO:
   ```bash
   # Using ImageMagick
   convert Figure_1_Multi_Food_Meal.png Figure_1_Multi_Food_Meal.tif
   ```

4. Include in patent application with figure descriptions

---

**All scripts create placeholder visualizations based on the detailed specifications in the .md files.**
