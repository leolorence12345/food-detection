# Manual GPU Testing - Step by step
# Run each section manually

Write-Host "=========================================="
Write-Host "Manual GPU Testing Guide"
Write-Host "=========================================="
Write-Host ""

# Step 1: Find AMI
Write-Host "Step 1: Finding Deep Learning AMI..."
$AMI_ID = aws ec2 describe-images `
    --owners amazon `
    --filters "Name=name,Values=Deep Learning AMI GPU PyTorch * (Ubuntu 22.04)*" "Name=state,Values=available" `
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' `
    --output text `
    --region us-east-1

if (-not $AMI_ID -or $AMI_ID -eq "None") {
    Write-Host "⚠️  Deep Learning AMI not found, using Amazon Linux..."
    $AMI_ID = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2023
}

Write-Host "AMI ID: $AMI_ID"
Write-Host ""

# Step 2: Get VPC/Subnet
Write-Host "Step 2: Getting VPC and subnet..."
$VPC_ID = aws ec2 describe-vpcs `
    --filters "Name=isDefault,Values=true" `
    --query 'Vpcs[0].VpcId' `
    --output text `
    --region us-east-1

$SUBNET_ID = aws ec2 describe-subnets `
    --filters "Name=vpc-id,Values=$VPC_ID" `
    --query 'Subnets[0].SubnetId' `
    --output text `
    --region us-east-1

Write-Host "VPC: $VPC_ID"
Write-Host "Subnet: $SUBNET_ID"
Write-Host ""

# Step 3: Create security group
Write-Host "Step 3: Creating security group..."
$MY_IP = (Invoke-WebRequest -Uri "https://checkip.amazonaws.com" -UseBasicParsing).Content.Trim()
Write-Host "Your IP: $MY_IP"

$SG_NAME = "gpu-test-sg-$(Get-Date -Format 'yyyyMMddHHmmss')"
$SECURITY_GROUP = aws ec2 create-security-group `
    --group-name $SG_NAME `
    --description "Temporary security group for GPU testing" `
    --vpc-id $VPC_ID `
    --query 'GroupId' `
    --output text `
    --region us-east-1

aws ec2 authorize-security-group-ingress `
    --group-id $SECURITY_GROUP `
    --protocol tcp `
    --port 22 `
    --cidr "$MY_IP/32" `
    --region us-east-1 | Out-Null

Write-Host "Security Group: $SECURITY_GROUP"
Write-Host ""

# Step 4: Launch instance
Write-Host "Step 4: Launching GPU instance..."
Write-Host "⚠️  This will cost ~`$0.526/hour"
Write-Host "Press Enter to continue or Ctrl+C to cancel..."
Read-Host

$INSTANCE_ID = aws ec2 run-instances `
    --image-id $AMI_ID `
    --instance-type g4dn.xlarge `
    --key-name nutrition-api-key `
    --security-group-ids $SECURITY_GROUP `
    --subnet-id $SUBNET_ID `
    --associate-public-ip-address `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=GPU-Test-Manual}]" `
    --query 'Instances[0].InstanceId' `
    --output text `
    --region us-east-1

Write-Host ""
Write-Host "=========================================="
Write-Host "Instance Launched!"
Write-Host "=========================================="
Write-Host "Instance ID: $INSTANCE_ID"
Write-Host "Security Group: $SECURITY_GROUP"
Write-Host ""
Write-Host "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region us-east-1

$PUBLIC_IP = aws ec2 describe-instances `
    --instance-ids $INSTANCE_ID `
    --query 'Reservations[0].Instances[0].PublicIpAddress' `
    --output text `
    --region us-east-1

Write-Host ""
Write-Host "=========================================="
Write-Host "Instance Ready!"
Write-Host "=========================================="
Write-Host "Instance ID: $INSTANCE_ID"
Write-Host "Public IP: $PUBLIC_IP"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Wait 2-3 minutes for instance to fully boot"
Write-Host "2. Try SSH: ssh -i ~/.ssh/nutrition-api-key.pem ubuntu@$PUBLIC_IP"
Write-Host "   Or: ssh -i ~/.ssh/nutrition-api-key.pem ec2-user@$PUBLIC_IP"
Write-Host "3. Once connected, run:"
Write-Host "   cd /home/ec2-user"
Write-Host "   git clone https://github.com/leolorence12345/food-detection.git"
Write-Host "   cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker"
Write-Host "   chmod +x test-gpu-simple.sh"
Write-Host "   ./test-gpu-simple.sh"
Write-Host ""
Write-Host "⚠️  IMPORTANT: Stop instance when done:"
Write-Host "   aws ec2 stop-instances --instance-ids $INSTANCE_ID --region us-east-1"
Write-Host ""

