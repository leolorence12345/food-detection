# Set the PATH to include user and machine environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "=== Checking Docker Build Progress ===" -ForegroundColor Cyan

$INSTANCE_ID = "i-0fdfdfb7ffe180e17"
$REGION = "us-east-1"

Write-Host "Instance ID: $INSTANCE_ID" -ForegroundColor Yellow
Write-Host "Fetching console output..." -ForegroundColor Yellow

# Get console output
$output = aws ec2 get-console-output --instance-id $INSTANCE_ID --region $REGION --output text 2>&1

if ($LASTEXITCODE -eq 0) {
    # Show last 50 lines
    $output | Select-Object -Last 50

    Write-Host "`n=== Build Status ===" -ForegroundColor Cyan
    if ($output -match "Build completed at") {
        Write-Host "Docker build COMPLETED!" -ForegroundColor Green
        Write-Host "`nReady to force ECS to use new image" -ForegroundColor Yellow
    } elseif ($output -match "Building Docker image") {
        Write-Host "Docker build IN PROGRESS..." -ForegroundColor Yellow
    } elseif ($output -match "Cloning") {
        Write-Host "Cloning repository..." -ForegroundColor Yellow
    } else {
        Write-Host "Initializing..." -ForegroundColor Yellow
    }
} else {
    Write-Host "Error fetching console output" -ForegroundColor Red
    Write-Host $output
}
