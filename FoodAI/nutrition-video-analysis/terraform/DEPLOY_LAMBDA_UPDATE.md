# Deploy Lambda Update - Two Options

## Option 1: Install Terraform (Recommended)

### Install Terraform on macOS:

```bash
# Using Homebrew (recommended)
brew install terraform

# Or download from: https://www.terraform.io/downloads
```

### Then deploy:

```bash
cd FoodAI/nutrition-video-analysis/terraform
terraform init  # Only needed first time
terraform apply  # Deploy Lambda update
```

## Option 2: Deploy Lambda Directly with AWS CLI (No Terraform needed)

If you don't want to install Terraform, you can deploy the Lambda function directly:

### Step 1: Create the Lambda deployment package

```bash
cd FoodAI/nutrition-video-analysis/terraform
zip -r results_handler.zip lambda_code/results_handler/
```

### Step 2: Update the Lambda function

```bash
# Replace with your actual Lambda function name
LAMBDA_NAME="nutrition-video-analysis-dev-results-handler"
REGION="us-east-1"

aws lambda update-function-code \
  --function-name $LAMBDA_NAME \
  --zip-file fileb://results_handler.zip \
  --region $REGION
```

### Step 3: Verify the update

```bash
aws lambda get-function \
  --function-name $LAMBDA_NAME \
  --region $REGION \
  --query 'Configuration.LastModified'
```

## Quick Check: Find Your Lambda Function Name

```bash
aws lambda list-functions \
  --region us-east-1 \
  --query 'Functions[?contains(FunctionName, `nutrition`) && contains(FunctionName, `results`)].FunctionName' \
  --output table
```

## What This Updates

- **Only** the `results_handler` Lambda function
- Adds segmented images URLs to API responses
- Does NOT affect the ECS service (already deployed)
- Takes ~30 seconds to deploy

## After Deployment

1. Test by processing a new image/video
2. Check API response includes `segmented_images` field
3. Frontend will automatically receive segmented image URLs
