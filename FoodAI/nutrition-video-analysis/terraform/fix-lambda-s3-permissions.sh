#!/bin/bash

# Fix Lambda S3 ListBucket Permission
# Updates the Lambda IAM policy to allow listing S3 buckets for segmented images

set -e

REGION="us-east-1"

echo "🔍 Finding Lambda execution role..."
ROLE_NAME=$(aws iam list-roles --region $REGION --query "Roles[?contains(RoleName, 'nutri-analysis-dev-lambda-exec')].RoleName" --output text | head -1)

if [ -z "$ROLE_NAME" ]; then
  echo "❌ Could not find Lambda execution role"
  exit 1
fi

echo "✅ Found role: $ROLE_NAME"
echo ""

echo "🔍 Finding Lambda custom policy..."
POLICY_ARN=$(aws iam list-policies --region $REGION --scope Local --query "Policies[?contains(PolicyName, 'nutrition') && contains(PolicyName, 'lambda-custom')].Arn" --output text | head -1)

if [ -z "$POLICY_ARN" ]; then
  echo "❌ Could not find Lambda custom policy"
  exit 1
fi

echo "✅ Found policy: $POLICY_ARN"
echo ""

echo "📋 Getting current policy version..."
CURRENT_VERSION=$(aws iam get-policy --policy-arn "$POLICY_ARN" --query 'Policy.DefaultVersionId' --output text)
CURRENT_POLICY=$(aws iam get-policy-version --policy-arn "$POLICY_ARN" --version-id "$CURRENT_VERSION" --query 'PolicyVersion.Document' --output json)

echo "Current policy has $(echo "$CURRENT_POLICY" | python3 -c "import sys, json; doc=json.load(sys.stdin); print(len([s for s in doc['Statement'] if 's3:ListBucket' in str(s)]))") statements with s3:ListBucket"
echo ""

# Get bucket ARNs
RESULTS_BUCKET=$(aws s3api list-buckets --region $REGION --query "Buckets[?contains(Name, 'nutrition') && contains(Name, 'results')].Name" --output text | head -1)
VIDEOS_BUCKET=$(aws s3api list-buckets --region $REGION --query "Buckets[?contains(Name, 'nutrition') && contains(Name, 'videos')].Name" --output text | head -1)
MODELS_BUCKET=$(aws s3api list-buckets --region $REGION --query "Buckets[?contains(Name, 'nutrition') && contains(Name, 'models')].Name" --output text | head -1)

if [ -z "$RESULTS_BUCKET" ]; then
  echo "❌ Could not find results bucket"
  exit 1
fi

RESULTS_BUCKET_ARN="arn:aws:s3:::${RESULTS_BUCKET}"
VIDEOS_BUCKET_ARN="arn:aws:s3:::${VIDEOS_BUCKET}"
MODELS_BUCKET_ARN="arn:aws:s3:::${MODELS_BUCKET}"

echo "📦 Buckets:"
echo "  Results: $RESULTS_BUCKET_ARN"
echo "  Videos: $VIDEOS_BUCKET_ARN"
echo "  Models: $MODELS_BUCKET_ARN"
echo ""

# Create updated policy with s3:ListBucket
UPDATED_POLICY=$(echo "$CURRENT_POLICY" | python3 << 'PYTHON_SCRIPT'
import sys, json

policy = json.load(sys.stdin)

# Check if ListBucket statement already exists
has_list_bucket = any(
    's3:ListBucket' in str(stmt.get('Action', [])) 
    for stmt in policy['Statement']
)

if has_list_bucket:
    print("✅ Policy already has s3:ListBucket permission")
    sys.exit(0)

# Add ListBucket statement
list_bucket_stmt = {
    "Effect": "Allow",
    "Action": ["s3:ListBucket"],
    "Resource": [
        "arn:aws:s3:::nutrition-video-analysis-dev-videos-*",
        "arn:aws:s3:::nutrition-video-analysis-dev-results-*",
        "arn:aws:s3:::nutrition-video-analysis-dev-models-*"
    ]
}

policy['Statement'].append(list_bucket_stmt)
print(json.dumps(policy, indent=2))
PYTHON_SCRIPT
)

if [ $? -eq 0 ] && [ -n "$UPDATED_POLICY" ] && [ "$UPDATED_POLICY" != "✅ Policy already has s3:ListBucket permission" ]; then
  echo "📝 Creating new policy version..."
  
  # Save to temp file
  echo "$UPDATED_POLICY" > /tmp/lambda-policy-update.json
  
  # Create new policy version
  aws iam create-policy-version \
    --policy-arn "$POLICY_ARN" \
    --policy-document file:///tmp/lambda-policy-update.json \
    --set-as-default \
    --region $REGION
  
  echo "✅ Policy updated successfully!"
  echo ""
  echo "🧪 Test by calling the results API again"
else
  echo "$UPDATED_POLICY"
fi
