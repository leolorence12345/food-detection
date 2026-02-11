# Frontend Update Guide - New Deployed Service

## Changes Made

### 1. Lambda Function Updated
- **File:** `lambda_code/results_handler/lambda_function.py`
- **Change:** Added segmented images URLs to API response
- **Status:** ✅ Code updated, needs deployment

### 2. Frontend API Service Updated
- **File:** `services/NutritionAnalysisAPI.ts`
- **Changes:**
  - Added `SegmentedImages` interface
  - Updated `NutritionAnalysisResult` to include `segmented_images`
  - Modified `getResults()` to always request detailed results
  - Modified `pollForResults()` to request detailed results by default
- **Status:** ✅ Updated

### 3. Data Model Updated
- **File:** `store/slices/historySlice.ts`
- **Changes:**
  - Added `SegmentedImage` and `SegmentedImages` interfaces
  - Updated `AnalysisEntry` to include `segmented_images` field
- **Status:** ✅ Updated

### 4. Preview Screen Updated
- **File:** `screens/PreviewScreen.tsx`
- **Changes:**
  - Stores `segmented_images` when saving analysis
- **Status:** ✅ Updated

## Architecture Explanation

### Two Separate Services:

1. **ECS Service (Docker Container)** ✅ Already Deployed
   - Processes videos/images using AI models
   - Uploads segmented images to S3
   - This is already working and creating segmented images

2. **Lambda Function (API Handler)** ⚠️ Needs Deployment
   - Handles frontend API requests (`/api/results/{job_id}`)
   - Returns job results including segmented image URLs
   - **Currently deployed version doesn't include segmented image URLs**
   - **Local code updated but not deployed to AWS yet**

### Why Lambda Update is Needed:

The ECS service creates and stores segmented images in S3, but the Lambda function that returns results to the frontend needs to be updated to include those image URLs in its response. Without the Lambda update, the frontend won't receive the segmented image URLs even though they exist in S3.

## Next Steps

### 1. Install Terraform (if not already installed)

**Quick install using Homebrew:**
```bash
brew install terraform
terraform version  # Verify installation
```

**For detailed installation instructions, see:** `INSTALL_TERRAFORM.md`

### 2. Deploy Lambda Update

**⚠️ Important:** If Terraform shows it's trying to create new resources (instead of updating), use the AWS CLI script instead to safely update only the Lambda function.

**Option A: Using AWS CLI Script (Recommended - Safer)**
```bash
cd FoodAI/nutrition-video-analysis/terraform
./deploy-lambda-update.sh
```

**Option B: Using Terraform (Only if state exists)**
```bash
cd FoodAI/nutrition-video-analysis/terraform

# Initialize Terraform (only needed first time)
terraform init

# Review what will be changed
terraform plan

# Deploy the Lambda function update
terraform apply
```

**When prompted, type `yes` (lowercase) to confirm.**

**Note:** This only updates the Lambda function, not the ECS service (which is already deployed).

**Lambda Function Name:** `nutrition-video-analysis-dev-results-handler`

### 2. Add UI to Display Segmented Images

You can add segmented image display in:
- **ResultsScreen.tsx** - Show overlay button on each card
- **MealDetailScreen.tsx** - Show overlay image in detail view

Example code to add:
```tsx
{item.segmented_images?.overlay_urls && item.segmented_images.overlay_urls.length > 0 && (
  <TouchableOpacity 
    onPress={() => {
      // Open overlay image
      const overlayUrl = item.segmented_images.overlay_urls[0].url;
      // Display in modal or navigate to image viewer
    }}
  >
    <Text>View Segmentation Overlay</Text>
  </TouchableOpacity>
)}
```

## API Endpoint

The frontend is already using the correct API Gateway:
- **URL:** `https://qx3i66fa87.execute-api.us-east-1.amazonaws.com/v1`
- **Status:** ✅ Active and working

## Testing

After deploying Lambda:
1. Process a new image/video
2. Check API response includes `segmented_images` field
3. Verify URLs are accessible
4. Add UI to display overlays
