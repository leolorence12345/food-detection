# GPU Deployment - Quick Reference

## Files Created/Modified

### New Files:
1. **`Dockerfile.gpu`** - GPU-enabled Docker image
2. **`test-gpu-on-ec2.sh`** - Automated GPU testing script
3. **`EC2_GPU_TESTING_GUIDE.md`** - Step-by-step EC2 testing guide
4. **`variables.tf`** - Terraform variables (moved from main.tf)
5. **`gpu-resources.tf`** - EC2 GPU infrastructure (ASG, Launch Template, etc.)
6. **`task-definition-gpu.tf`** - GPU-enabled ECS task definition
7. **`service-gpu.tf`** - GPU-enabled ECS service with auto-scaling
8. **`gpu-user-data.sh`** - EC2 instance initialization script
9. **`GPU_DEPLOYMENT_GUIDE.md`** - Complete deployment guide
10. **`terraform.tfvars.example`** - Example configuration file

### Modified Files:
- **`main.tf`** - Still contains CPU/Fargate configuration (unchanged)
- Variables moved to separate `variables.tf` for better organization

## Quick Start

### 1. Test GPU Locally on EC2
```bash
# Follow EC2_GPU_TESTING_GUIDE.md
# This will verify GPU works before deployment
```

### 2. Build and Push GPU Image
```bash
cd terraform/docker
docker build -f Dockerfile.gpu -t nutrition-gpu:latest .
# Tag and push to ECR (see GPU_DEPLOYMENT_GUIDE.md)
```

### 3. Deploy with GPU
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: set use_gpu = true, device_type = "cuda"
terraform init
terraform plan
terraform apply
```

## Architecture

### CPU Mode (Default)
- **Service**: `nutrition-video-analysis-dev-video-processor`
- **Task Definition**: `nutrition-video-analysis-dev-video-processor`
- **Launch Type**: Fargate
- **Image**: `Dockerfile` (CPU version)

### GPU Mode
- **Service**: `nutrition-video-analysis-dev-video-processor-gpu`
- **Task Definition**: `nutrition-video-analysis-dev-video-processor-gpu`
- **Launch Type**: EC2 (g4dn.xlarge or g5.xlarge)
- **Image**: `Dockerfile.gpu` (GPU version)

## Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `use_gpu` | `false` | Enable GPU mode |
| `device_type` | `"cpu"` | `"cpu"` or `"cuda"` |
| `gpu_instance_type` | `"g4dn.xlarge"` | EC2 instance type |
| `docker_image_tag` | `"latest"` | Docker image tag |
| `gpu_min_capacity` | `0` | Min GPU instances |
| `gpu_max_capacity` | `5` | Max GPU instances |

## Switching Modes

### Enable GPU:
```hcl
use_gpu = true
device_type = "cuda"
docker_image_tag = "gpu-test"  # or "latest"
```

### Disable GPU (back to CPU):
```hcl
use_gpu = false
device_type = "cpu"
docker_image_tag = "latest"
```

## Cost Comparison

| Mode | Instance | Cost/Hour | 40 Frames | Cost/Video |
|------|----------|-----------|----------|------------|
| CPU | Fargate | $0.04 | 13 min | $0.009 |
| GPU | g4dn.xlarge | $0.526 | 2 min | $0.018 |

**Note**: GPU is 6x faster but 2x more expensive per video. For high volume, GPU can be more cost-effective due to faster turnaround.

## Next Steps

1. ✅ Test GPU on EC2 (follow `EC2_GPU_TESTING_GUIDE.md`)
2. ✅ Build and push GPU Docker image
3. ✅ Update `terraform.tfvars` with GPU settings
4. ✅ Run `terraform apply`
5. ✅ Monitor CloudWatch logs for GPU confirmation
6. ✅ Test video processing performance

## Troubleshooting

See `GPU_DEPLOYMENT_GUIDE.md` for detailed troubleshooting steps.

Common issues:
- GPU instances not starting → Check AMI availability
- Tasks not running → Check task definition GPU requirements
- Image pull errors → Verify ECR image tag

