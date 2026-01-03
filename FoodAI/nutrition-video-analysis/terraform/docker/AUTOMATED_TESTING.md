# Automated GPU Testing

These scripts automatically launch an EC2 GPU instance, run tests, and report results.

## Prerequisites

1. **AWS CLI configured** with credentials
2. **SSH key pair** in AWS (and locally at `~/.ssh/key-name.pem`)
3. **Permissions** to launch EC2 instances

## Quick Start

### Linux/Mac:

```bash
cd food-detection/FoodAI/nutrition-video-analysis/terraform/docker

# Set your key pair name
export AWS_KEY_PAIR=your-key-pair-name

# Make script executable
chmod +x launch-and-test-gpu.sh

# Run (launches instance, runs tests, reports results)
./launch-and-test-gpu.sh
```

### Windows (PowerShell):

```powershell
cd food-detection\FoodAI\nutrition-video-analysis\terraform\docker

# Set your key pair name
$env:AWS_KEY_PAIR = "your-key-pair-name"

# Run
.\run-gpu-test.ps1
```

## What It Does

1. ✅ Finds latest Deep Learning AMI
2. ✅ Creates temporary security group
3. ✅ Launches g4dn.xlarge GPU instance
4. ✅ Waits for instance to be ready
5. ✅ Copies test script to instance
6. ✅ Runs full GPU test suite
7. ✅ Reports pass/fail
8. ⚠️  **Reminds you to stop/terminate instance**

## Manual Steps (If Automated Fails)

If the automated script fails, follow `QUICK_TEST_COMMANDS.md` for manual steps.

## Cost

- **g4dn.xlarge**: ~$0.526/hour
- **Test duration**: ~20-30 minutes
- **Total cost**: ~$0.18-0.26 per test run

**⚠️ IMPORTANT**: Always stop/terminate the instance after testing!

```bash
# Stop (can restart later)
aws ec2 stop-instances --instance-ids i-xxxxx --region us-east-1

# Terminate (permanent)
aws ec2 terminate-instances --instance-ids i-xxxxx --region us-east-1
```

## Troubleshooting

### "Key pair not found"
- Verify key pair exists in AWS: `aws ec2 describe-key-pairs`
- Check key file exists locally: `ls ~/.ssh/your-key.pem`

### "Insufficient permissions"
- Need: `ec2:RunInstances`, `ec2:CreateSecurityGroup`, `ec2:DescribeInstances`

### "SSH connection timeout"
- Check security group allows your IP
- Wait longer (instances can take 3-5 minutes to fully boot)

### "Tests fail"
- Check instance logs via AWS Console
- SSH into instance manually and debug
- See `QUICK_TEST_COMMANDS.md` for manual testing

## Expected Output

```
==========================================
GPU Testing Script
==========================================

Step 1: Checking GPU...
✅ NVIDIA driver found
[GPU info from nvidia-smi]

Step 2: Checking Docker...
✅ Docker GPU access working!

Step 3: Preparing code...
[Cloning repo...]

Step 4: Building GPU Docker image...
[Building... takes 15-20 min]

Step 5: Testing GPU in container...
============================================================
GPU TEST RESULTS
============================================================
PyTorch version: 2.1.0+cu118
CUDA available: True
CUDA version: 11.8
GPU count: 1
GPU name: Tesla T4
GPU memory: 15.75 GB
✅ GPU TEST PASSED!

==========================================
✅ ALL TESTS PASSED!
==========================================
```

## Next Steps After Tests Pass

1. **Push image to ECR** (see commands in test output)
2. **Update terraform.tfvars**: Set `use_gpu = true`
3. **Deploy**: `terraform apply`
4. **Monitor**: Check CloudWatch logs for GPU confirmation

