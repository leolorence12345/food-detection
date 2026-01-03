# Launch GPU instance without prompts
# This will launch immediately

$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host "Launching GPU Instance"
Write-Host "=========================================="
Write-Host ""

# Find AMI
Write-Host "Finding AMI..."
$AMI_ID = aws ec2 describe-images `
    --owners amazon `
    --filters "Name=name,Values=Deep Learning AMI GPU PyTorch * (Ubuntu 22.04)*" "Name=state,Values=available" `
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' `
    --output text `
    --region us-east-1

if (-not $AMI_ID -or $AMI_ID -eq "None") {
    Write-Host "Using Amazon Linux 2023..."
    $AMI_ID = "ami-0c55b159cbfafe1f0"
}

Write-Host "AMI: $AMI_ID"

# Get VPC/Subnet
Write-Host "Getting VPC..."
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

# Create security group
Write-Host "Creating security group..."
$MY_IP = (Invoke-WebRequest -Uri "https://checkip.amazonaws.com" -UseBasicParsing).Content.Trim()
$SG_NAME = "gpu-test-$(Get-Date -Format 'yyyyMMddHHmmss')"

$SECURITY_GROUP = aws ec2 create-security-group `
    --group-name $SG_NAME `
    --description "GPU test security group" `
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

# Launch instance
Write-Host ""
Write-Host "Launching g4dn.xlarge instance (~`$0.526/hour)..."
Write-Host ""

$INSTANCE_ID = aws ec2 run-instances `
    --image-id $AMI_ID `
    --instance-type g4dn.xlarge `
    --key-name nutrition-api-key `
    --security-group-ids $SECURITY_GROUP `
    --subnet-id $SUBNET_ID `
    --associate-public-ip-address `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=GPU-Test}]" `
    --query 'Instances[0].InstanceId' `
    --output text `
    --region us-east-1

Write-Host "Instance ID: $INSTANCE_ID"
Write-Host "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region us-east-1

$INSTANCE_INFO = aws ec2 describe-instances `
    --instance-ids $INSTANCE_ID `
    --query 'Reservations[0].Instances[0]' `
    --region us-east-1 | ConvertFrom-Json

$PUBLIC_IP = $INSTANCE_INFO.PublicIpAddress
$STATE = $INSTANCE_INFO.State.Name

Write-Host ""
Write-Host "=========================================="
Write-Host "✅ Instance Launched!"
Write-Host "=========================================="
Write-Host "Instance ID: $INSTANCE_ID"
Write-Host "Public IP: $PUBLIC_IP"
Write-Host "State: $STATE"
Write-Host "Security Group: $SECURITY_GROUP"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "1. Wait 2-3 minutes for instance to fully boot"
Write-Host "2. Connect via AWS Systems Manager (no SSH key needed):"
Write-Host "   aws ssm start-session --target $INSTANCE_ID --region us-east-1"
Write-Host ""
Write-Host "3. Or download SSH key from AWS Console and connect:"
Write-Host "   ssh -i ~/.ssh/nutrition-api-key.pem ubuntu@$PUBLIC_IP"
Write-Host "   (or ec2-user@$PUBLIC_IP for Amazon Linux)"
Write-Host ""
Write-Host "4. Once connected, run:"
Write-Host "   git clone https://github.com/leolorence12345/food-detection.git"
Write-Host "   cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker"
Write-Host "   chmod +x test-gpu-simple.sh"
Write-Host "   ./test-gpu-simple.sh"
Write-Host ""
Write-Host "⚠️  IMPORTANT: Stop instance when done:"
Write-Host "   aws ec2 stop-instances --instance-ids $INSTANCE_ID --region us-east-1"
Write-Host ""

# Save instance info
@{
    InstanceId = $INSTANCE_ID
    PublicIP = $PUBLIC_IP
    SecurityGroup = $SECURITY_GROUP
    LaunchTime = Get-Date
} | ConvertTo-Json | Out-File "gpu-instance-info.json"

Write-Host "Instance info saved to: gpu-instance-info.json"

