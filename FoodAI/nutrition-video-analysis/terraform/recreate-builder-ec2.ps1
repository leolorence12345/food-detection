# Set the PATH to include user and machine environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "=== Recreating EC2 Builder Instance ===" -ForegroundColor Cyan

cd "d:\Nutrition5k\food-detection\FoodAI\nutrition-video-analysis\terraform"

Write-Host "`nStep 1: Destroying old EC2 instance..." -ForegroundColor Yellow
terraform destroy "-auto-approve" "-target=aws_instance.docker_push_temp"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Old instance destroyed successfully" -ForegroundColor Green
} else {
    Write-Host "Warning: Destroy failed or no instance to destroy" -ForegroundColor Yellow
}

Write-Host "`nStep 2: Creating new EC2 instance with corrected configuration..." -ForegroundColor Yellow
terraform apply "-auto-approve" "-target=aws_instance.docker_push_temp"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nNew EC2 instance created successfully!" -ForegroundColor Green

    $instanceId = terraform output -raw docker_push_instance_id
    Write-Host "Instance ID: $instanceId" -ForegroundColor Yellow

    Write-Host "`n=== Instance Details ===" -ForegroundColor Cyan
    Write-Host "The instance will automatically:" -ForegroundColor White
    Write-Host "1. Install Docker and Git" -ForegroundColor White
    Write-Host "2. Clone from: https://github.com/leolorence12345/food-detection.git" -ForegroundColor White
    Write-Host "3. Build Docker image from: food-detection/FoodAI/nutrition-video-analysis/terraform/docker" -ForegroundColor White
    Write-Host "4. Push to ECR (10-15 minutes)" -ForegroundColor White

    Write-Host "`n=== Monitoring ===" -ForegroundColor Cyan
    Write-Host "Starting automated monitoring script..." -ForegroundColor Yellow

    # Start monitoring in background
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File monitor-and-deploy.ps1" -WorkingDirectory (Get-Location)

    Write-Host "`nMonitoring script started in new window" -ForegroundColor Green
    Write-Host "It will auto-deploy when build completes" -ForegroundColor Green
} else {
    Write-Host "`nFailed to create EC2 instance" -ForegroundColor Red
}
