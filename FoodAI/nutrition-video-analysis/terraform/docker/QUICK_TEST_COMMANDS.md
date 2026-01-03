# Quick GPU Testing Commands

Copy-paste these commands to test GPU on EC2.

## Step 1: Launch EC2 GPU Instance

### AWS Console:
1. EC2 → Launch Instance
2. AMI: **Deep Learning AMI (Ubuntu 22.04)** or **Amazon Linux 2023**
3. Instance: **g4dn.xlarge**
4. Security Group: Allow SSH (port 22) from your IP
5. Launch

### AWS CLI:
```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type g4dn.xlarge \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx
```

## Step 2: Connect to Instance

```bash
ssh -i your-key.pem ec2-user@<instance-ip>
# Or for Ubuntu:
ssh -i your-key.pem ubuntu@<instance-ip>
```

## Step 3: Run Test Script

```bash
# Download and run test script
cd /home/ec2-user
curl -O https://raw.githubusercontent.com/leolorence12345/food-detection/main/FoodAI/nutrition-video-analysis/terraform/docker/test-gpu-simple.sh
chmod +x test-gpu-simple.sh
./test-gpu-simple.sh
```

**OR** clone repo and run:

```bash
cd /home/ec2-user
git clone https://github.com/leolorence12345/food-detection.git
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker
chmod +x test-gpu-simple.sh
./test-gpu-simple.sh
```

## Step 4: Manual Testing (if script fails)

### Check GPU:
```bash
nvidia-smi
```

### Install Docker:
```bash
# Amazon Linux
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
newgrp docker

# Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -a -G docker ubuntu
newgrp docker
```

### Install NVIDIA Container Toolkit:
```bash
# Ubuntu
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Amazon Linux (if available)
sudo yum install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Test Docker GPU:
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Build GPU Image:
```bash
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker
docker build -f Dockerfile.gpu -t nutrition-gpu:test .
```

### Test PyTorch GPU:
```bash
docker run --rm --gpus all nutrition-gpu:test \
    python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### Run Full GPU Test:
```bash
docker run --rm --gpus all -v $(pwd):/test nutrition-gpu:test \
    python3 /test/test-pytorch-gpu.py
```

## Step 5: Push to ECR (if tests pass)

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    185329004895.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag nutrition-gpu:test \
    185329004895.dkr.ecr.us-east-1.amazonaws.com/nutrition-video-analysis-dev-video-processor:gpu-test

# Push
docker push \
    185329004895.dkr.ecr.us-east-1.amazonaws.com/nutrition-video-analysis-dev-video-processor:gpu-test
```

## Expected Output

### nvidia-smi:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx.xx   Driver Version: 535.xx.xx   CUDA Version: 12.x    |
+-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
+===============================+======================+======================+
|   0  Tesla T4           Off   | 00000000:00:1E.0 Off |                    0 |
```

### PyTorch Test:
```
============================================================
PyTorch GPU Test
============================================================

PyTorch version: 2.1.0+cu118
CUDA available: True
CUDA version: 11.8
cuDNN version: 8500

GPU Information:
  Device count: 1

  GPU 0: Tesla T4
    Memory: 15.75 GB
    Compute Capability: 7.5

============================================================
Testing GPU Computation
============================================================
✅ GPU computation test passed!
   Result tensor shape: torch.Size([1000, 1000])
   Result tensor device: cuda:0

============================================================
✅ ALL GPU TESTS PASSED!
============================================================
```

## Troubleshooting

### "nvidia-smi: command not found"
- Not a GPU instance, or drivers not installed
- Use Deep Learning AMI (has drivers pre-installed)

### "Docker: unknown flag: --gpus"
- NVIDIA Container Toolkit not installed
- Install it (see Step 4)

### "CUDA not available" in PyTorch
- Check PyTorch CUDA version matches system CUDA
- Verify GPU is accessible: `nvidia-smi`
- Check Docker GPU access: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`

### Build fails
- Check internet connection (needs to download packages)
- Verify Dockerfile.gpu exists
- Check disk space: `df -h`

## Cleanup

**IMPORTANT**: Stop/terminate instance when done!

```bash
# From your local machine
aws ec2 stop-instances --instance-ids i-xxxxx
# Or terminate:
aws ec2 terminate-instances --instance-ids i-xxxxx
```

