#!/bin/bash

# Deploy Lambda Update - Results Handler with Segmented Images Support
# This script updates the Lambda function without requiring Terraform

set -e

REGION="us-east-1"
LAMBDA_DIR="lambda_code/results_handler"
ZIP_FILE="results_handler.zip"

echo "🔍 Finding Lambda function name..."
LAMBDA_NAME=$(aws lambda list-functions \
  --region $REGION \
  --query 'Functions[?contains(FunctionName, `nutrition`) && contains(FunctionName, `results`)].FunctionName' \
  --output text | head -1)

if [ -z "$LAMBDA_NAME" ]; then
  echo "❌ Error: Could not find results handler Lambda function"
  echo "Available functions:"
  aws lambda list-functions --region $REGION --query 'Functions[?contains(FunctionName, `nutrition`)].FunctionName' --output table
  exit 1
fi

echo "✅ Found Lambda function: $LAMBDA_NAME"
echo ""

echo "📦 Creating deployment package..."
cd "$(dirname "$0")"
rm -f $ZIP_FILE
cd $LAMBDA_DIR
zip -r ../$ZIP_FILE . -x "*.pyc" "__pycache__/*" "*.DS_Store" > /dev/null
cd ..
echo "✅ Package created: $ZIP_FILE"
echo ""

echo "🚀 Deploying Lambda function..."
aws lambda update-function-code \
  --function-name "$LAMBDA_NAME" \
  --zip-file "fileb://$ZIP_FILE" \
  --region $REGION \
  --output json > /tmp/lambda-update.json

echo "✅ Lambda function updated!"
echo ""

echo "⏳ Waiting for update to complete..."
aws lambda wait function-updated \
  --function-name "$LAMBDA_NAME" \
  --region $REGION

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Update details:"
aws lambda get-function \
  --function-name "$LAMBDA_NAME" \
  --region $REGION \
  --query '{FunctionName:Configuration.FunctionName,LastModified:Configuration.LastModified,Version:Configuration.Version}' \
  --output table

echo ""
echo "🧪 Test the update by processing a new image/video and checking for 'segmented_images' in the API response."
