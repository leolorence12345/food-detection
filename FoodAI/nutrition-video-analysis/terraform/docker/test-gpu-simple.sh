#!/bin/bash
# Simple GPU test script - run this on EC2 GPU instance
set -e

echo "=========================================="
echo "GPU Testing Script"
echo "=========================================="

# Step 1: Check GPU
echo ""
echo "Step 1: Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA driver found"
    nvidia-smi
else
    echo "❌ ERROR: nvidia-smi not found!"
    exit 1
fi

# Step 2: Check Docker
echo ""
echo "Step 2: Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    echo "⚠️  Run: newgrp docker (or log out/in)"
    exit 1
fi

# Test Docker GPU access
echo "Testing Docker GPU access..."
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi || {
    echo "❌ Docker cannot access GPU"
    echo "Installing NVIDIA Container Toolkit..."
    
    # Install NVIDIA Container Toolkit
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - 2>/dev/null || \
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-docker.gpg
    
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
        sudo tee /etc/apt/sources.list.d/nvidia-docker.list 2>/dev/null || \
        echo "deb [signed-by=/usr/share/keyrings/nvidia-docker.gpg] https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list" | \
        sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    
    sudo apt-get update || sudo yum update -y
    sudo apt-get install -y nvidia-container-toolkit || sudo yum install -y nvidia-container-toolkit
    sudo systemctl restart docker
    
    # Test again
    docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi || {
        echo "❌ Still cannot access GPU. Check installation."
        exit 1
    }
}

echo "✅ Docker GPU access working!"

# Step 3: Clone repo if needed
echo ""
echo "Step 3: Preparing code..."
if [ ! -d "food-detection" ]; then
    echo "Cloning repository..."
    cd /home/ec2-user
    git clone https://github.com/leolorence12345/food-detection.git
fi

cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Step 4: Build GPU image
echo ""
echo "Step 4: Building GPU Docker image..."
echo "This will take 15-20 minutes..."
docker build -f Dockerfile.gpu -t nutrition-gpu:test .

# Step 5: Test GPU in container
echo ""
echo "Step 5: Testing GPU in container..."
docker run --rm --gpus all nutrition-gpu:test \
    python3 -c "
import torch
print('=' * 50)
print('GPU TEST RESULTS')
print('=' * 50)
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB')
    print('✅ GPU TEST PASSED!')
else:
    print('❌ GPU TEST FAILED - CUDA not available')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ ALL TESTS PASSED!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Push image to ECR (see commands below)"
    echo "2. Update terraform.tfvars with use_gpu = true"
    echo "3. Run terraform apply"
    echo ""
else
    echo ""
    echo "❌ TESTS FAILED"
    exit 1
fi

