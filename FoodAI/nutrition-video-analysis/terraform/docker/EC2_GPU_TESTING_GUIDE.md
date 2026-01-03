# EC2 GPU Testing Guide

This guide walks you through testing GPU support on an EC2 GPU instance before updating the deployment.

## Prerequisites

- AWS account with permissions to launch EC2 instances
- AWS CLI configured
- Basic knowledge of EC2 and Docker

## Step 1: Launch EC2 GPU Instance

### Option A: AWS Console
1. Go to EC2 Console → Launch Instance
2. Choose **Deep Learning AMI (Ubuntu)** or **Amazon Linux 2023**
3. Instance type: **g4dn.xlarge** (cheapest GPU option, ~$0.526/hr)
   - Or **g5.xlarge** for better performance (~$1.006/hr)
4. Configure security group:
   - Allow SSH (port 22) from your IP
   - Allow HTTP/HTTPS if needed
5. Create/select a key pair
6. Launch instance

### Option B: AWS CLI
```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \  # Amazon Linux 2023 (update with actual AMI)
  --instance-type g4dn.xlarge \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=GPU-Test}]'
```

## Step 2: Connect to EC2 Instance

```bash
ssh -i your-key.pem ec2-user@<instance-public-ip>
# Or for Ubuntu:
ssh -i your-key.pem ubuntu@<instance-public-ip>
```

## Step 3: Verify GPU

```bash
# Check NVIDIA driver
nvidia-smi

# Should show GPU info like:
# NVIDIA-SMI 535.xx.xx
# Driver Version: 535.xx.xx
# CUDA Version: 12.x
```

## Step 4: Setup Docker with GPU Support

### For Amazon Linux 2023:
```bash
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo yum install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### For Ubuntu:
```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -a -G docker ubuntu

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Step 5: Clone Repository and Build GPU Image

```bash
cd /home/ec2-user  # or /home/ubuntu

# Clone repository
git clone https://github.com/leolorence12345/food-detection.git
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Make test script executable
chmod +x test-gpu-on-ec2.sh

# Run automated setup (or do manually)
./test-gpu-on-ec2.sh
```

## Step 6: Manual Build (Alternative)

If the script doesn't work, build manually:

```bash
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Build GPU image
docker build -f Dockerfile.gpu -t nutrition-gpu:latest .

# Test GPU in container
docker run --rm --gpus all nutrition-gpu:latest \
    python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

## Step 7: Test with Actual Video Processing

```bash
# Set environment variables
export DEVICE=cuda
export S3_VIDEOS_BUCKET=nutrition-video-analysis-dev-videos-dbenpoj2
export S3_RESULTS_BUCKET=nutrition-video-analysis-dev-results-dbenpoj2
export S3_MODELS_BUCKET=nutrition-video-analysis-dev-models-dbenpoj2
export SQS_VIDEO_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/185329004895/nutrition-video-analysis-dev-video-processing
export DYNAMODB_JOBS_TABLE=nutrition-video-analysis-dev-jobs
export AWS_REGION=us-east-1

# Configure AWS credentials (if not using IAM role)
aws configure

# Run worker (will process from SQS queue)
docker run --rm --gpus all \
    -e DEVICE=cuda \
    -e S3_VIDEOS_BUCKET=$S3_VIDEOS_BUCKET \
    -e S3_RESULTS_BUCKET=$S3_RESULTS_BUCKET \
    -e S3_MODELS_BUCKET=$S3_MODELS_BUCKET \
    -e SQS_VIDEO_QUEUE_URL=$SQS_VIDEO_QUEUE_URL \
    -e DYNAMODB_JOBS_TABLE=$DYNAMODB_JOBS_TABLE \
    -e AWS_REGION=$AWS_REGION \
    -v ~/.aws:/root/.aws:ro \
    nutrition-gpu:latest
```

## Step 8: Monitor Performance

Compare CPU vs GPU:

**CPU (current):**
- SAM2 propagation: ~21 seconds/frame
- 40 frames: ~13 minutes

**GPU (expected):**
- SAM2 propagation: ~0.5-2 seconds/frame
- 40 frames: ~30 seconds - 2 minutes

Watch logs for:
```
Device: cuda
CUDA available: True
GPU: NVIDIA T4 (or similar)
```

## Step 9: Push to ECR (for deployment testing)

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    185329004895.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag nutrition-gpu:latest \
    185329004895.dkr.ecr.us-east-1.amazonaws.com/nutrition-video-analysis-dev-video-processor:gpu-test

docker push \
    185329004895.dkr.ecr.us-east-1.amazonaws.com/nutrition-video-analysis-dev-video-processor:gpu-test
```

## Step 10: Clean Up

**IMPORTANT:** Stop/terminate the EC2 instance when done to avoid charges!

```bash
# From your local machine
aws ec2 stop-instances --instance-ids i-xxxxx
# Or terminate if you don't need it:
aws ec2 terminate-instances --instance-ids i-xxxxx
```

## Troubleshooting

### GPU not detected in container
- Verify `nvidia-smi` works on host
- Check NVIDIA Container Toolkit is installed
- Restart Docker: `sudo systemctl restart docker`
- Try: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`

### PyTorch CUDA not available
- Check PyTorch version matches CUDA version
- Verify CUDA libraries in container: `ldconfig -p | grep cuda`

### Out of memory
- Use smaller batch sizes
- Process fewer frames
- Consider g5.xlarge (more GPU memory)

## Next Steps

Once GPU testing is successful:
1. Update Terraform to use EC2 launch type
2. Create ECS cluster with GPU instances
3. Update task definition with GPU requirements
4. Change DEVICE env var to "cuda"
5. Deploy!

