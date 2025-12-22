# Set the PATH to include user and machine environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "=== Creating EC2 instance for Docker build ===" -ForegroundColor Cyan

cd "d:\Nutrition5k\food-detection\FoodAI\nutrition-video-analysis\terraform"

# Run terraform apply
terraform apply "-auto-approve" "-target=aws_instance.docker_push_temp"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nEC2 instance created successfully!" -ForegroundColor Green
    Write-Host "`nGetting instance details..." -ForegroundColor Yellow

    terraform output docker_push_instance_id
    terraform output docker_push_instance_public_ip

    Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "The instance will automatically:" -ForegroundColor Yellow
    Write-Host "1. Clone the repository from GitHub" -ForegroundColor White
    Write-Host "2. Build the Docker image (10-15 minutes)" -ForegroundColor White
    Write-Host "3. Push to ECR" -ForegroundColor White

    Write-Host "`nMonitor build progress:" -ForegroundColor Cyan
    Write-Host "terraform output docker_push_log_command | Invoke-Expression" -ForegroundColor White
} else {
    Write-Host "`nFailed to create EC2 instance" -ForegroundColor Red
}
