# GPU Deployment Guide

This guide explains how to deploy the nutrition video analysis system with GPU support using EC2 instances.

## Overview

The system supports two deployment modes:
- **CPU Mode (Default)**: Uses AWS Fargate - no GPU, lower cost, slower processing
- **GPU Mode**: Uses EC2 instances with GPU - higher cost, much faster processing

## Prerequisites

1. ✅ Tested GPU Docker image on EC2 (see `EC2_GPU_TESTING_GUIDE.md`)
2. ✅ GPU Docker image pushed to ECR with tag (e.g., `gpu-test` or `latest`)
3. ✅ AWS account with permissions to create EC2 instances, ECS clusters, etc.

## Architecture

### CPU Mode (Current)
- **Launch Type**: Fargate
- **Instance**: Managed by AWS (no EC2 instances)
- **Cost**: ~$0.04/hour per task
- **Performance**: ~21 seconds/frame

### GPU Mode
- **Launch Type**: EC2
- **Instance Type**: g4dn.xlarge (or g5.xlarge)
- **Cost**: ~$0.526/hour per instance (g4dn.xlarge)
- **Performance**: ~0.5-2 seconds/frame

## Deployment Steps

### Step 1: Update Variables

Create or update `terraform.tfvars`:

```hcl
# Enable GPU mode
use_gpu = true

# GPU configuration
gpu_instance_type = "g4dn.xlarge"  # or "g5.xlarge"
device_type = "cuda"
docker_image_tag = "gpu-test"  # or "latest" if you pushed GPU image as latest

# Optional: Specify GPU AMI (leave empty to auto-detect Deep Learning AMI)
# gpu_instance_ami = "ami-xxxxx"

# GPU scaling
gpu_min_capacity = 0  # Start with 0, scale up when needed
gpu_max_capacity = 5  # Maximum GPU instances

# Other variables
aws_region = "us-east-1"
project_name = "nutrition-video-analysis"
environment = "dev"
gemini_api_key = "your-key-here"
```

### Step 2: Add Missing Variable

Add to `variables.tf` if not present:

```hcl
variable "gpu_key_pair_name" {
  description = "EC2 Key Pair name for GPU instances (optional, for SSH access)"
  type        = string
  default     = ""
}
```

### Step 3: Build and Push GPU Image

On your EC2 GPU test instance:

```bash
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Build GPU image
docker build -f Dockerfile.gpu -t nutrition-gpu:latest .

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

### Step 4: Initialize Terraform

```bash
cd food-detection/FoodAI/nutrition-video-analysis/terraform

# Initialize (if first time)
terraform init

# Review changes
terraform plan -var-file=terraform.tfvars
```

### Step 5: Apply Changes

```bash
# Apply GPU resources
terraform apply -var-file=terraform.tfvars
```

This will create:
- EC2 Auto Scaling Group with GPU instances
- ECS Capacity Provider for GPU
- GPU-enabled task definition
- GPU-enabled ECS service
- Auto-scaling policies

### Step 6: Verify Deployment

```bash
# Check ECS cluster
aws ecs describe-clusters --clusters nutrition-video-analysis-dev-cluster

# Check GPU instances
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=nutrition-video-analysis-dev-gpu-instance" \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name]'

# Check ECS service
aws ecs describe-services \
  --cluster nutrition-video-analysis-dev-cluster \
  --services nutrition-video-analysis-dev-video-processor-gpu

# Check CloudWatch logs
aws logs tail /ecs/nutrition-video-analysis-dev-video-processor --follow
```

### Step 7: Test Processing

Submit a test video job and monitor:

```bash
# Watch logs for GPU confirmation
aws logs tail /ecs/nutrition-video-analysis-dev-video-processor --follow | grep -i "cuda\|gpu\|device"
```

Look for:
```
Device: cuda
CUDA available: True
GPU: NVIDIA T4 (or similar)
```

## Switching Between CPU and GPU

### Switch to GPU Mode

1. Update `terraform.tfvars`:
   ```hcl
   use_gpu = true
   device_type = "cuda"
   docker_image_tag = "gpu-test"
   ```

2. Apply:
   ```bash
   terraform apply -var-file=terraform.tfvars
   ```

3. The CPU service will scale to 0, GPU service will be active

### Switch Back to CPU Mode

1. Update `terraform.tfvars`:
   ```hcl
   use_gpu = false
   device_type = "cpu"
   docker_image_tag = "latest"
   ```

2. Apply:
   ```bash
   terraform apply -var-file=terraform.tfvars
   ```

3. GPU instances will terminate, CPU service will be active

## Cost Comparison

### CPU Mode (Fargate)
- **Per Task**: ~$0.04/hour (4 vCPU, 16GB)
- **40 frames (13 min)**: ~$0.009 per video
- **100 videos/day**: ~$0.90/day

### GPU Mode (EC2 g4dn.xlarge)
- **Per Instance**: ~$0.526/hour
- **40 frames (2 min)**: ~$0.018 per video (but 6x faster)
- **100 videos/day**: ~$1.80/day (but processes faster, can handle more)

**Note**: GPU mode is more expensive but processes videos 10-20x faster. For high-volume processing, GPU can be more cost-effective due to faster turnaround.

## Troubleshooting

### GPU Instances Not Starting

1. **Check AMI**: Verify Deep Learning AMI is available in your region
   ```bash
   aws ec2 describe-images \
     --owners amazon \
     --filters "Name=name,Values=Deep Learning AMI GPU PyTorch*"
   ```

2. **Check Instance Limits**: GPU instances may require limit increase
   ```bash
   aws service-quotas get-service-quota \
     --service-code ec2 \
     --quota-code L-3819A6DF
   ```

3. **Check User Data**: Verify user-data script runs correctly
   ```bash
   # SSH into instance and check logs
   sudo cat /var/log/cloud-init-output.log
   ```

### Tasks Not Running on GPU

1. **Check Task Definition**: Verify `resourceRequirements` includes GPU
   ```bash
   aws ecs describe-task-definition \
     --task-definition nutrition-video-analysis-dev-video-processor-gpu \
     --query 'taskDefinition.containerDefinitions[0].resourceRequirements'
   ```

2. **Check Instance Type**: Verify instances match `gpu_instance_type`
   ```bash
   aws ec2 describe-instances \
     --filters "Name=tag:Name,Values=*gpu*" \
     --query 'Reservations[*].Instances[*].InstanceType'
   ```

### Docker Image Issues

1. **Verify Image Tag**: Ensure correct tag is pushed
   ```bash
   aws ecr describe-images \
     --repository-name nutrition-video-analysis-dev-video-processor \
     --image-ids imageTag=gpu-test
   ```

2. **Check Image Architecture**: Must be linux/amd64
   ```bash
   docker inspect <image> | grep Architecture
   ```

## Monitoring

### Key Metrics

1. **ECS Service Metrics**:
   - `CPUUtilization`
   - `MemoryUtilization`
   - `RunningTaskCount`

2. **EC2 Instance Metrics**:
   - `CPUUtilization`
   - `GPUUtilization` (if CloudWatch agent installed)
   - `NetworkIn/Out`

3. **SQS Queue Metrics**:
   - `ApproximateNumberOfMessagesVisible`
   - `ApproximateNumberOfMessagesNotVisible`

### CloudWatch Dashboards

Create a dashboard to monitor:
- GPU instance count
- Task execution time
- Queue depth
- Error rates

## Cleanup

To remove GPU resources:

```bash
# Set use_gpu = false in terraform.tfvars
terraform apply -var-file=terraform.tfvars

# Or destroy everything
terraform destroy -var-file=terraform.tfvars
```

**Important**: GPU instances cost money even when idle. Always set `gpu_min_capacity = 0` if not processing videos continuously.

