# =============================================================================
# GPU ECS SERVICE
# Service configuration for GPU-enabled tasks
# =============================================================================

resource "aws_ecs_service" "video_processor_gpu" {
  count = var.use_gpu ? 1 : 0

  name            = "${local.name_prefix}-video-processor-gpu"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.video_processor_gpu[0].arn
  desired_count   = 0  # Scale from 0 - starts when messages arrive

  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.gpu[0].name
    weight            = 100
    base              = 0
  }

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 0

  # Placement constraints to ensure tasks run on GPU instances
  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.instance-type =~ ${var.gpu_instance_type}"
  }

  tags = {
    Name = "${local.name_prefix}-video-processor-gpu-service"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# Auto Scaling Target for GPU service
resource "aws_appautoscaling_target" "ecs_target_gpu" {
  count = var.use_gpu ? 1 : 0

  max_capacity       = var.gpu_max_capacity
  min_capacity       = var.gpu_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.video_processor_gpu[0].name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_scale_up_gpu" {
  count = var.use_gpu ? 1 : 0

  name               = "${local.name_prefix}-scale-up-gpu"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_target_gpu[0].resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target_gpu[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target_gpu[0].service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_lower_bound = 0
      scaling_adjustment          = 1
    }
  }
}

resource "aws_appautoscaling_policy" "ecs_scale_down_gpu" {
  count = var.use_gpu ? 1 : 0

  name               = "${local.name_prefix}-scale-down-gpu"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_target_gpu[0].resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target_gpu[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target_gpu[0].service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 300
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1
    }
  }
}

# CloudWatch Alarm for SQS Queue Depth (GPU)
resource "aws_cloudwatch_metric_alarm" "sqs_messages_visible_gpu" {
  count = var.use_gpu ? 1 : 0

  alarm_name          = "${local.name_prefix}-sqs-queue-depth-gpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Trigger scale-up when messages are in queue"
  alarm_actions       = [aws_appautoscaling_policy.ecs_scale_up_gpu[0].arn]

  dimensions = {
    QueueName = aws_sqs_queue.video_processing.name
  }

  tags = {
    Name = "${local.name_prefix}-sqs-queue-depth-gpu-alarm"
  }
}

