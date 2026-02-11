# Install Terraform on macOS

## Option 1: Using Homebrew (Recommended - Easiest)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Terraform
brew install terraform

# Verify installation
terraform version
```

## Option 2: Manual Installation

### Step 1: Download Terraform

1. Visit: https://www.terraform.io/downloads
2. Download the macOS AMD64 or Apple Silicon version (depending on your Mac)
3. Extract the zip file

### Step 2: Install Terraform

```bash
# Move to a directory in your PATH (e.g., /usr/local/bin)
sudo mv terraform /usr/local/bin/

# Or add to your PATH by adding to ~/.zshrc:
echo 'export PATH="$PATH:/path/to/terraform/directory"' >> ~/.zshrc
source ~/.zshrc

# Verify installation
terraform version
```

## Option 3: Using tfenv (Version Manager)

If you want to manage multiple Terraform versions:

```bash
# Install tfenv
brew install tfenv

# Install latest Terraform
tfenv install latest

# Use latest version
tfenv use latest

# Verify
terraform version
```

## Verify Installation

After installation, verify it works:

```bash
terraform version
# Should output something like: Terraform v1.6.0
```

## Next Steps: Deploy Lambda Update

Once Terraform is installed:

```bash
cd FoodAI/nutrition-video-analysis/terraform

# Initialize Terraform (only needed first time)
terraform init

# Review what will be changed
terraform plan

# Deploy the Lambda update
terraform apply
```

When prompted, type `yes` to confirm the deployment.

## Troubleshooting

### If you get "command not found" after installation:

1. Check if Terraform is in your PATH:
   ```bash
   which terraform
   echo $PATH
   ```

2. Add Terraform to your PATH:
   ```bash
   # For zsh (default on macOS)
   echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.zshrc
   source ~/.zshrc
   ```

### If you get permission errors:

```bash
# Make sure Terraform is executable
chmod +x /usr/local/bin/terraform

# Or use sudo if needed
sudo chmod +x /usr/local/bin/terraform
```
