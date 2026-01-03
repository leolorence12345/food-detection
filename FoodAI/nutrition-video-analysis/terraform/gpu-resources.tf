# =============================================================================
# GPU RESOURCES (EC2 Launch Type)
# Only created when use_gpu = true
# =============================================================================

# Data source for Deep Learning AMI (if not specified)
data "aws_ami" "gpu_ami" {
  count = var.use_gpu && var.gpu_instance_ami == "" ? 1 : 0

  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["Deep Learning AMI GPU PyTorch * (Ubuntu 22.04)*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ECS Capacity Provider for GPU instances
resource "aws_ecs_capacity_provider" "gpu" {
  count = var.use_gpu ? 1 : 0
  name  = "${local.name_prefix}-gpu-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.gpu[0].arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      status          = "ENABLED"
      target_capacity = 100
      minimum_scaling_step_size = 1
      maximum_scaling_step_size = 1
    }
  }

  tags = {
    Name = "${local.name_prefix}-gpu-capacity-provider"
  }
}

# Launch Template for GPU instances
resource "aws_launch_template" "gpu" {
  count = var.use_gpu ? 1 : 0

  name_prefix   = "${local.name_prefix}-gpu-"
  image_id      = var.gpu_instance_ami != "" ? var.gpu_instance_ami : data.aws_ami.gpu_ami[0].id
  instance_type = var.gpu_instance_type

  vpc_security_group_ids = [aws_security_group.ecs_tasks.id]

  # Optional: Add key pair for SSH access (only if provided)
  key_name = var.gpu_key_pair_name != "" ? var.gpu_key_pair_name : null

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_gpu[0].name
  }

  user_data = base64encode(templatefile("${path.module}/gpu-user-data.sh", {
    cluster_name = aws_ecs_cluster.main.name
    region       = var.aws_region
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${local.name_prefix}-gpu-instance"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group for GPU instances
resource "aws_autoscaling_group" "gpu" {
  count = var.use_gpu ? 1 : 0

  name                = "${local.name_prefix}-gpu-asg"
  vpc_zone_identifier = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  min_size            = var.gpu_min_capacity
  max_size            = var.gpu_max_capacity
  desired_capacity     = var.gpu_min_capacity

  launch_template {
    id      = aws_launch_template.gpu[0].id
    version = "$Latest"
  }

  health_check_type         = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Name"
    value               = "${local.name_prefix}-gpu-instance"
    propagate_at_launch = true
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = "true"
    propagate_at_launch = true
  }
}

# IAM Instance Profile for GPU EC2 instances
resource "aws_iam_role" "ecs_gpu_instance" {
  count = var.use_gpu ? 1 : 0
  name  = "${local.name_prefix}-ecs-gpu-instance"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${local.name_prefix}-ecs-gpu-instance-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_gpu_instance_ecs" {
  count      = var.use_gpu ? 1 : 0
  role       = aws_iam_role.ecs_gpu_instance[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role_policy_attachment" "ecs_gpu_instance_ssm" {
  count      = var.use_gpu ? 1 : 0
  role       = aws_iam_role.ecs_gpu_instance[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ecs_gpu" {
  count = var.use_gpu ? 1 : 0
  name  = "${local.name_prefix}-ecs-gpu-instance-profile"
  role  = aws_iam_role.ecs_gpu_instance[0].name

  tags = {
    Name = "${local.name_prefix}-ecs-gpu-instance-profile"
  }
}

# Update cluster capacity providers to include GPU
resource "aws_ecs_cluster_capacity_providers" "gpu" {
  count = var.use_gpu ? 1 : 0

  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = [aws_ecs_capacity_provider.gpu[0].name]

  default_capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.gpu[0].name
    weight            = 100
    base              = 0
  }
}

