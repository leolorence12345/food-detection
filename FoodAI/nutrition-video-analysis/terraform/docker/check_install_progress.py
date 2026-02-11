#!/usr/bin/env python3
"""Quick script to check installation progress"""
import subprocess
import sys
from pathlib import Path

# Read requirements
req_file = Path(__file__).parent / "requirements.txt"
required = []
with open(req_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            # Extract package name (before == or >=)
            pkg = line.split("==")[0].split(">=")[0].split("<")[0].strip()
            if pkg:
                required.append(pkg.lower())

# Get installed packages
try:
    result = subprocess.run(
        ["pip", "list", "--format=freeze"],
        capture_output=True,
        text=True,
        check=True
    )
    installed = {}
    for line in result.stdout.split("\n"):
        if "==" in line:
            pkg, version = line.split("==", 1)
            installed[pkg.lower()] = version
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Check progress
installed_count = 0
missing = []

for req in required:
    # Check if installed (handle package name variations)
    found = False
    for inst_pkg in installed.keys():
        if req in inst_pkg or inst_pkg in req:
            found = True
            installed_count += 1
            break
    
    if not found:
        missing.append(req)

total = len(required)
progress = (installed_count / total * 100) if total > 0 else 0

print("=" * 60)
print(f"📦 Installation Progress: {installed_count}/{total} packages ({progress:.1f}%)")
print("=" * 60)
print(f"\n✅ Installed: {installed_count}")
print(f"❌ Missing: {len(missing)}")
print(f"\n📋 Missing packages:")
for pkg in missing[:10]:  # Show first 10
    print(f"   - {pkg}")
if len(missing) > 10:
    print(f"   ... and {len(missing) - 10} more")

print(f"\n💡 To install remaining packages:")
print(f"   pip install -r requirements.txt")


