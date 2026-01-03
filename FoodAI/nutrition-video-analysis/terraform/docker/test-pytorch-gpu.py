#!/usr/bin/env python3
"""
Quick PyTorch GPU test script
Run this inside the GPU Docker container to verify GPU works
"""
import torch
import sys

print("=" * 60)
print("PyTorch GPU Test")
print("=" * 60)

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    print("\n❌ ERROR: CUDA is not available!")
    print("Possible issues:")
    print("  - GPU not detected")
    print("  - CUDA drivers not installed")
    print("  - PyTorch CUDA version mismatch")
    sys.exit(1)

print(f"CUDA version: {torch.version.cuda}")
print(f"cuDNN version: {torch.backends.cudnn.version()}")
print(f"\nGPU Information:")
print(f"  Device count: {torch.cuda.device_count()}")

for i in range(torch.cuda.device_count()):
    props = torch.cuda.get_device_properties(i)
    print(f"\n  GPU {i}: {props.name}")
    print(f"    Memory: {props.total_memory / 1024**3:.2f} GB")
    print(f"    Compute Capability: {props.major}.{props.minor}")

# Test GPU computation
print("\n" + "=" * 60)
print("Testing GPU Computation")
print("=" * 60)

try:
    # Create tensors on GPU
    device = torch.device("cuda:0")
    x = torch.randn(1000, 1000).to(device)
    y = torch.randn(1000, 1000).to(device)
    
    # Perform matrix multiplication
    z = torch.matmul(x, y)
    
    print("✅ GPU computation test passed!")
    print(f"   Result tensor shape: {z.shape}")
    print(f"   Result tensor device: {z.device}")
    
except Exception as e:
    print(f"❌ GPU computation test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL GPU TESTS PASSED!")
print("=" * 60)

