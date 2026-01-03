# PowerShell script to launch EC2 GPU instance and run tests
# Run this from Windows with AWS CLI configured

$ErrorActionPreference = "Stop"

$REGION = "us-east-1"
$INSTANCE_TYPE = "g4dn.xlarge"
$KEY_NAME = $env:AWS_KEY_PAIR
if (-not $KEY_NAME) {
    Write-Host "❌ Set AWS_KEY_PAIR environment variable or edit script"
    exit 1
}

Write-Host "=========================================="
Write-Host "Automated GPU Testing Setup"
Write-Host "=========================================="
Write-Host ""

# Check AWS CLI
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI not found. Install it first."
    exit 1
}

# Get latest Deep Learning AMI
Write-Host "Finding latest Deep Learning AMI..."
$AMI_ID = aws ec2 describe-images `
    --owners amazon `
    --filters "Name=name,Values=Deep Learning AMI GPU PyTorch * (Ubuntu 22.04)*" "Name=state,Values=available" `
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' `
    --output text `
    --region $REGION

if (-not $AMI_ID -or $AMI_ID -eq "None") {
    Write-Host "⚠️  Deep Learning AMI not found, trying Amazon Linux..."
    $AMI_ID = aws ec2 describe-images `
        --owners amazon `
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" `
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' `
        --output text `
        --region $REGION
}

Write-Host "Using AMI: $AMI_ID"
Write-Host ""

# Get default VPC and subnet
Write-Host "Getting VPC and subnet..."
$VPC_ID = aws ec2 describe-vpcs `
    --filters "Name=isDefault,Values=true" `
    --query 'Vpcs[0].VpcId' `
    --output text `
    --region $REGION

$SUBNET_ID = aws ec2 describe-subnets `
    --filters "Name=vpc-id,Values=$VPC_ID" `
    --query 'Subnets[0].SubnetId' `
    --output text `
    --region $REGION

Write-Host "VPC: $VPC_ID"
Write-Host "Subnet: $SUBNET_ID"
Write-Host ""

# Create security group
Write-Host "Creating temporary security group..."
$SG_NAME = "gpu-test-sg-$(Get-Date -Format 'yyyyMMddHHmmss')"
$SECURITY_GROUP = aws ec2 create-security-group `
    --group-name $SG_NAME `
    --description "Temporary security group for GPU testing" `
    --vpc-id $VPC_ID `
    --query 'GroupId' `
    --output text `
    --region $REGION

# Allow SSH
$MY_IP = (Invoke-WebRequest -Uri "https://checkip.amazonaws.com" -UseBasicParsing).Content.Trim()
aws ec2 authorize-security-group-ingress `
    --group-id $SECURITY_GROUP `
    --protocol tcp `
    --port 22 `
    --cidr "$MY_IP/32" `
    --region $REGION | Out-Null

Write-Host "Created security group: $SECURITY_GROUP"
Write-Host "⚠️  Remember to delete this security group after testing!"
Write-Host ""

# Launch instance
Write-Host "Launching GPU instance..."
Write-Host "Instance type: $INSTANCE_TYPE"
Write-Host "This will cost ~`$0.526/hour. Press Ctrl+C to cancel in 5 seconds..."
Start-Sleep -Seconds 5

$INSTANCE_ID = aws ec2 run-instances `
    --image-id $AMI_ID `
    --instance-type $INSTANCE_TYPE `
    --key-name $KEY_NAME `
    --security-group-ids $SECURITY_GROUP `
    --subnet-id $SUBNET_ID `
    --associate-public-ip-address `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=GPU-Test}]" `
    --query 'Instances[0].InstanceId' `
    --output text `
    --region $REGION

Write-Host "Instance launched: $INSTANCE_ID"
Write-Host ""

# Wait for instance
Write-Host "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
$PUBLIC_IP = aws ec2 describe-instances `
    --instance-ids $INSTANCE_ID `
    --query 'Reservations[0].Instances[0].PublicIpAddress' `
    --output text `
    --region $REGION

Write-Host "Instance IP: $PUBLIC_IP"
Write-Host ""

# Wait for SSH
Write-Host "Waiting for SSH to be ready (this may take 2-3 minutes)..."
$MAX_RETRIES = 30
$RETRY = 0
$SSH_READY = $false

while ($RETRY -lt $MAX_RETRIES -and -not $SSH_READY) {
    try {
        $null = ssh -i "$env:USERPROFILE\.ssh\$KEY_NAME.pem" -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@$PUBLIC_IP "echo 'SSH ready'" 2>&1
        $USER = "ubuntu"
        $SSH_READY = $true
    } catch {
        try {
            $null = ssh -i "$env:USERPROFILE\.ssh\$KEY_NAME.pem" -o StrictHostKeyChecking=no -o ConnectTimeout=5 ec2-user@$PUBLIC_IP "echo 'SSH ready'" 2>&1
            $USER = "ec2-user"
            $SSH_READY = $true
        } catch {
            Write-Host "Waiting... ($RETRY/$MAX_RETRIES)"
            Start-Sleep -Seconds 10
            $RETRY++
        }
    }
}

if (-not $SSH_READY) {
    Write-Host "❌ SSH not ready after $MAX_RETRIES attempts"
    Write-Host "Instance ID: $INSTANCE_ID"
    Write-Host "Public IP: $PUBLIC_IP"
    exit 1
}

Write-Host "SSH is ready! Using user: $USER"
Write-Host ""

# Copy and run test
Write-Host "=========================================="
Write-Host "Running GPU tests on instance..."
Write-Host "=========================================="
Write-Host ""

$SSH_KEY = "$env:USERPROFILE\.ssh\$KEY_NAME.pem"

# Copy test script
scp -i $SSH_KEY -o StrictHostKeyChecking=no test-gpu-simple.sh ${USER}@${PUBLIC_IP}:/tmp/

# Run test
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${USER}@${PUBLIC_IP} @"
cd /tmp
chmod +x test-gpu-simple.sh
cd /home/$USER
git clone https://github.com/leolorence12345/food-detection.git 2>/dev/null || echo 'Repo exists'
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker
cp /tmp/test-gpu-simple.sh .
chmod +x test-gpu-simple.sh
./test-gpu-simple.sh
"@

$TEST_RESULT = $LASTEXITCODE

Write-Host ""
Write-Host "=========================================="
if ($TEST_RESULT -eq 0) {
    Write-Host "✅ TESTS PASSED!"
} else {
    Write-Host "❌ TESTS FAILED!"
}
Write-Host "=========================================="
Write-Host ""
Write-Host "Instance details:"
Write-Host "  Instance ID: $INSTANCE_ID"
Write-Host "  Public IP: $PUBLIC_IP"
Write-Host "  SSH: ssh -i $SSH_KEY $USER@$PUBLIC_IP"
Write-Host ""
Write-Host "⚠️  IMPORTANT: Stop or terminate the instance when done:"
Write-Host "  aws ec2 stop-instances --instance-ids $INSTANCE_ID --region $REGION"
Write-Host "  aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
Write-Host ""

exit $TEST_RESULT

