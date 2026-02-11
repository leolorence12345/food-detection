# RAG Data Files Download Guide

## Required Files

The nutrition analysis system requires three RAG (Retrieval-Augmented Generation) data files:

1. **ap815e.pdf** - USDA Food Density Database (PDF)
2. **FNDDS.xlsx** - Food and Nutrient Database for Dietary Studies (Excel)
3. **CoFID.xlsx** - Composition of Foods Integrated Dataset (Excel)

## Download Instructions

### 1. FNDDS.xlsx

**Source:** USDA FoodData Central
- **URL:** https://fdc.nal.usda.gov/download-datasets
- **Steps:**
  1. Go to the download page
  2. Select "FNDDS" dataset
  3. Choose "2021-2023" version
  4. Download in CSV or JSON format
  5. If CSV, convert to Excel (.xlsx) format
  6. Save as `FNDDS.xlsx`

**Alternative:** Direct download link (if available):
- Check: https://www.ars.usda.gov/northeast-area/beltsville-md-bhnrc/beltsville-human-nutrition-research-center/food-surveys-research-group/docs/fndds-download-databases/

### 2. CoFID.xlsx

**Source:** UK Government Public Health England
- **URL:** https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid
- **Steps:**
  1. Go to the UK government page
  2. Find "CoFID Excel file" (4.42 MB)
  3. Click download
  4. Save as `CoFID.xlsx`

### 3. ap815e.pdf

**Source:** USDA Agricultural Research Service
- **Note:** This file may be archived or have a different name
- **Search:** USDA food density database PDF
- **Alternative:** The system has fallback densities, so this file is optional but recommended for better accuracy

## Upload to S3

Once you have downloaded the files, upload them to S3:

```bash
# Set variables
S3_BUCKET="nutrition-video-analysis-dev-models-dbenpoj2"
REGION="us-east-1"

# Upload files
aws s3 cp /path/to/ap815e.pdf s3://${S3_BUCKET}/rag/ap815e.pdf --region ${REGION}
aws s3 cp /path/to/FNDDS.xlsx s3://${S3_BUCKET}/rag/FNDDS.xlsx --region ${REGION}
aws s3 cp /path/to/CoFID.xlsx s3://${S3_BUCKET}/rag/CoFID.xlsx --region ${REGION}

# Verify upload
aws s3 ls s3://${S3_BUCKET}/rag/ --region ${REGION}
```

## Current Status

- ✅ Worker code updated to download RAG files from S3
- ⏳ Files need to be manually downloaded and uploaded
- ✅ System works with fallback data (but less accurate)

## After Upload

Once files are uploaded:
1. The next ECS task will automatically download them
2. Nutrition analysis will use the full databases
3. Results will be more accurate
