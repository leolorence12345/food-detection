"""
Full test of cached_download monkey patch with actual SentenceTransformer initialization
This simulates what happens in the real deployment
"""
import sys
import os

# Add the current directory to path to import nutrition_rag_system
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("TESTING FULL cached_download MONKEY PATCH")
print("=" * 60)

# Import nutrition_rag_system which applies the monkey patch
print("\n1. Importing nutrition_rag_system (applies monkey patch)...")
try:
    import nutrition_rag_system
    print("   ✅ nutrition_rag_system imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Verify the monkey patch is applied
print("\n2. Verifying monkey patch is applied...")
try:
    import huggingface_hub
    if hasattr(huggingface_hub, 'cached_download'):
        print("   ✅ cached_download is available in huggingface_hub")
    else:
        print("   ❌ cached_download is NOT available!")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error checking monkey patch: {e}")
    sys.exit(1)

# Test actual SentenceTransformer initialization
print("\n3. Testing SentenceTransformer initialization with 'all-MiniLM-L6-v2'...")
print("   This will call cached_download internally...")
try:
    from sentence_transformers import SentenceTransformer
    
    # This should trigger cached_download calls
    print("   Initializing SentenceTransformer...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("   ✅ SentenceTransformer initialized successfully!")
    
    # Test encoding to make sure it works
    print("\n4. Testing model encoding...")
    test_text = "This is a test sentence"
    embedding = model.encode(test_text)
    print(f"   ✅ Encoding successful! Embedding shape: {embedding.shape}")
    
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe monkey patch works correctly with SentenceTransformer!")
print("Safe to deploy Build #69")

