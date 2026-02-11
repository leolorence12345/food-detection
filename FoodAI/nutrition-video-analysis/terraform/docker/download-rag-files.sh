#!/bin/bash
# Script to download RAG data files and upload to S3
set -e

REGION="us-east-1"
S3_BUCKET="nutrition-video-analysis-dev-models-dbenpoj2"
TEMP_DIR="/tmp/rag_downloads"

mkdir -p "$TEMP_DIR/rag"
cd "$TEMP_DIR"

echo "=== Downloading RAG Data Files ==="

# 1. Download FNDDS (Food and Nutrient Database for Dietary Studies)
echo ""
echo "1. Downloading FNDDS..."
echo "   Note: FNDDS is available from USDA FoodData Central"
echo "   URL: https://fdc.nal.usda.gov/download-datasets"
echo "   Please download FNDDS 2021-2023 and save as FNDDS.xlsx"
echo "   Or download CSV and convert to Excel"

# 2. Download CoFID (UK Composition of Foods Integrated Dataset)
echo ""
echo "2. Downloading CoFID..."
COFID_URL="https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid"
echo "   URL: $COFID_URL"
echo "   Please download the Excel file (4.42 MB) and save as CoFID.xlsx"

# 3. Download ap815e.pdf (USDA Food Density)
echo ""
echo "3. Downloading ap815e.pdf..."
echo "   This file may need to be obtained from USDA archives"
echo "   Alternative: Use fallback densities (already implemented in code)"

echo ""
echo "=== Manual Download Required ==="
echo "Please download the files manually and place them in: $TEMP_DIR/rag/"
echo ""
echo "Files needed:"
echo "  - FNDDS.xlsx (from https://fdc.nal.usda.gov/download-datasets)"
echo "  - CoFID.xlsx (from https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid)"
echo "  - ap815e.pdf (USDA food density document - optional, fallback available)"
echo ""
echo "Once files are in $TEMP_DIR/rag/, run:"
echo "  aws s3 cp $TEMP_DIR/rag/ s3://$S3_BUCKET/rag/ --recursive --region $REGION"
