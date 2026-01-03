#!/bin/bash
# User data script for GPU EC2 instances
# Installs ECS agent and NVIDIA Container Toolkit
# Works with both Amazon Linux and Ubuntu

set -e

# Variables from Terraform
CLUSTER_NAME="${cluster_name}"
REGION="${region}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    OS="amzn"  # Default to Amazon Linux
fi

# Update system
if [ "$OS" = "ubuntu" ]; then
    apt-get update -y
    apt-get upgrade -y
else
    yum update -y
fi

# Install Docker
if [ "$OS" = "ubuntu" ]; then
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ubuntu
else
    yum install -y docker
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
fi

# Install ECS agent
if [ "$OS" = "ubuntu" ]; then
    # For Ubuntu, install ECS agent manually
    mkdir -p /var/lib/ecs
    curl -o /tmp/ecs-agent.tar https://s3.amazonaws.com/amazon-ecs-agent-us-east-1/ecs-agent-latest.tar
    docker load -i /tmp/ecs-agent.tar
else
    # For Amazon Linux, use yum package
    yum install -y ecs-init
fi

# Configure ECS
mkdir -p /etc/ecs
echo ECS_CLUSTER=$CLUSTER_NAME >> /etc/ecs/ecs.config
echo ECS_ENABLE_GPU_SUPPORT=true >> /etc/ecs/ecs.config
echo ECS_AVAILABLE_LOGGING_DRIVERS='["json-file","awslogs"]' >> /etc/ecs/ecs.config

# Install NVIDIA Container Toolkit
if [ "$OS" = "ubuntu" ]; then
    distribution=$ID$VERSION_ID
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
        tee /etc/apt/sources.list.d/nvidia-docker.list
    apt-get update
    apt-get install -y nvidia-container-toolkit
else
    # For Amazon Linux, use yum (if available) or install manually
    yum install -y nvidia-container-toolkit 2>/dev/null || {
        # Fallback: install manually
        distribution="rhel8"
        curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | \
            tee /etc/yum.repos.d/nvidia-docker.repo
        yum install -y nvidia-container-toolkit
    }
fi

# Restart Docker
systemctl restart docker

# Verify GPU (may not be available immediately on first boot)
nvidia-smi || echo "Warning: nvidia-smi not available yet (drivers may still be installing)"

# Start ECS agent
if [ "$OS" = "ubuntu" ]; then
    # Start ECS agent container
    docker run --name ecs-agent \
        --detach=true \
        --restart=on-failure:10 \
        --volume=/var/run/docker.sock:/var/run/docker.sock \
        --volume=/var/log/ecs:/log \
        --volume=/var/lib/ecs/data:/data \
        --env-file=/etc/ecs/ecs.config \
        amazon/amazon-ecs-agent:latest
else
    # Amazon Linux uses systemd service
    systemctl enable ecs
    systemctl start ecs
fi

# Log completion
echo "GPU instance setup complete at $(date)" >> /var/log/gpu-setup.log
echo "OS: $OS $VERSION" >> /var/log/gpu-setup.log
echo "Cluster: $CLUSTER_NAME" >> /var/log/gpu-setup.log

