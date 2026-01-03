#!/bin/bash
# Automated GPU Testing - Launches EC2 instance and runs tests
# Run this from your local machine with AWS CLI configured

set -e

REGION="us-east-1"
INSTANCE_TYPE="g4dn.xlarge"
KEY_NAME="${AWS_KEY_PAIR:-your-key-pair}"  # Set AWS_KEY_PAIR env var or edit this
SECURITY_GROUP="${AWS_SECURITY_GROUP:-}"   # Set AWS_SECURITY_GROUP env var or edit this

echo "=========================================="
echo "Automated GPU Testing Setup"
echo "=========================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Install it first."
    exit 1
fi

# Get latest Deep Learning AMI
echo ""
echo "Finding latest Deep Learning AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters \
        "Name=name,Values=Deep Learning AMI GPU PyTorch * (Ubuntu 22.04)*" \
        "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text \
    --region $REGION)

if [ "$AMI_ID" == "None" ] || [ -z "$AMI_ID" ]; then
    echo "⚠️  Deep Learning AMI not found, trying Amazon Linux..."
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters \
            "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
            "Name=state,Values=available" \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text \
        --region $REGION)
fi

echo "Using AMI: $AMI_ID"

# Get default VPC and subnet
echo ""
echo "Getting VPC and subnet..."
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' \
    --output text \
    --region $REGION)

SUBNET_ID=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[0].SubnetId' \
    --output text \
    --region $REGION)

echo "VPC: $VPC_ID"
echo "Subnet: $SUBNET_ID"

# Create security group if not provided
if [ -z "$SECURITY_GROUP" ]; then
    echo ""
    echo "Creating temporary security group..."
    SECURITY_GROUP=$(aws ec2 create-security-group \
        --group-name gpu-test-sg-$(date +%s) \
        --description "Temporary security group for GPU testing" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text \
        --region $REGION)
    
    # Allow SSH
    MY_IP=$(curl -s https://checkip.amazonaws.com)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP \
        --protocol tcp \
        --port 22 \
        --cidr $MY_IP/32 \
        --region $REGION
    
    echo "Created security group: $SECURITY_GROUP"
    echo "⚠️  Remember to delete this security group after testing!"
fi

# Create IAM role for EC2 (if needed)
echo ""
echo "Checking IAM role..."
IAM_ROLE=""
# You can create a role here or use existing one

# Launch instance
echo ""
echo "Launching GPU instance..."
echo "Instance type: $INSTANCE_TYPE"
echo "This will cost ~$0.526/hour. Press Ctrl+C to cancel in 5 seconds..."
sleep 5

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP \
    --subnet-id $SUBNET_ID \
    --associate-public-ip-address \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=GPU-Test-$(date +%s)}]" \
    --query 'Instances[0].InstanceId' \
    --output text \
    --region $REGION)

echo "Instance launched: $INSTANCE_ID"

# Wait for instance to be running
echo ""
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region $REGION)

echo "Instance IP: $PUBLIC_IP"

# Wait for SSH to be ready
echo ""
echo "Waiting for SSH to be ready (this may take 2-3 minutes)..."
MAX_RETRIES=30
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if ssh -i ~/.ssh/$KEY_NAME.pem -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        ubuntu@$PUBLIC_IP "echo 'SSH ready'" 2>/dev/null || \
        ssh -i ~/.ssh/$KEY_NAME.pem -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        ec2-user@$PUBLIC_IP "echo 'SSH ready'" 2>/dev/null; then
        echo "SSH is ready!"
        break
    fi
    echo "Waiting... ($RETRY/$MAX_RETRIES)"
    sleep 10
    RETRY=$((RETRY + 1))
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo "❌ SSH not ready after $MAX_RETRIES attempts"
    echo "Instance ID: $INSTANCE_ID"
    echo "Public IP: $PUBLIC_IP"
    exit 1
fi

# Determine user (ubuntu or ec2-user)
if ssh -i ~/.ssh/$KEY_NAME.pem -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "echo test" 2>/dev/null; then
    USER="ubuntu"
else
    USER="ec2-user"
fi

echo "Using user: $USER"

# Copy test script
echo ""
echo "Copying test script to instance..."
scp -i ~/.ssh/$KEY_NAME.pem -o StrictHostKeyChecking=no \
    test-gpu-simple.sh \
    $USER@$PUBLIC_IP:/tmp/

# Run test
echo ""
echo "=========================================="
echo "Running GPU tests on instance..."
echo "=========================================="
echo ""

ssh -i ~/.ssh/$KEY_NAME.pem -o StrictHostKeyChecking=no $USER@$PUBLIC_IP << 'ENDSSH'
cd /tmp
chmod +x test-gpu-simple.sh

# Clone repo and run test
cd /home/$USER
git clone https://github.com/leolorence12345/food-detection.git || echo "Repo already exists"
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker
cp /tmp/test-gpu-simple.sh .
chmod +x test-gpu-simple.sh
./test-gpu-simple.sh
ENDSSH

TEST_RESULT=$?

echo ""
echo "=========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ TESTS PASSED!"
else
    echo "❌ TESTS FAILED!"
fi
echo "=========================================="
echo ""
echo "Instance details:"
echo "  Instance ID: $INSTANCE_ID"
echo "  Public IP: $PUBLIC_IP"
echo "  SSH: ssh -i ~/.ssh/$KEY_NAME.pem $USER@$PUBLIC_IP"
echo ""
echo "⚠️  IMPORTANT: Stop or terminate the instance when done:"
echo "  aws ec2 stop-instances --instance-ids $INSTANCE_ID --region $REGION"
echo "  aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
echo ""

exit $TEST_RESULT

