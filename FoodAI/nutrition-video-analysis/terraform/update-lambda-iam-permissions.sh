#!/bin/bash

# Update Lambda IAM Policy to add s3:ListBucket permission
# This allows the results handler Lambda to list segmented images in S3

set -e

REGION="us-east-1"
POLICY_NAME=$(aws iam list-policies --region $REGION --scope Local --query "Policies[?contains(PolicyName, 'nutrition') && contains(PolicyName, 'lambda-custom')].PolicyName" --output text | head -1)

if [ -z "$POLICY_NAME" ]; then
  echo "❌ Could not find Lambda custom policy"
  exit 1
fi

POLICY_ARN=$(aws iam list-policies --region $REGION --scope Local --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text)

echo "Found policy: $POLICY_NAME"
echo "Policy ARN: $POLICY_ARN"
echo ""

echo "📋 Current policy:"
aws iam get-policy-version --policy-arn "$POLICY_ARN" --version-id $(aws iam get-policy --policy-arn "$POLICY_ARN" --query 'Policy.DefaultVersionId' --output text) --query 'PolicyVersion.Document' --output json | python3 -m json.tool

echo ""
echo "⚠️  To add s3:ListBucket permission, you need to:"
echo "1. Update the Terraform configuration (main.tf) - already done"
echo "2. Run: terraform apply (or use AWS Console to update the policy manually)"
echo ""
echo "Or update via AWS CLI:"
echo "aws iam put-role-policy --role-name <lambda-role-name> --policy-name s3-list-bucket --policy-document file://policy.json"
