#!/usr/bin/env python3
"""
Test script to run pipeline on an image locally and track Gemini API calls
"""
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Settings
from app.models import ModelManager
from app.pipeline import NutritionVideoPipeline
import logging

# Set up logging to track Gemini calls
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Track Gemini API calls
gemini_call_count = 0
gemini_calls = []

def track_gemini_call(function_name, details=""):
    """Track Gemini API calls"""
    global gemini_call_count
    gemini_call_count += 1
    gemini_calls.append({
        'call_number': gemini_call_count,
        'function': function_name,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })
    print(f"🔵 Gemini Call #{gemini_call_count}: {function_name} - {details}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_image_local.py <image_path>")
        print("Example: python test_image_local.py /path/to/image.jpg")
        sys.exit(1)
    
    image_path_str = sys.argv[1]
    image_path = Path(image_path_str)
    
    if not image_path.exists():
        print(f"Error: Image not found: {image_path_str}")
        sys.exit(1)
    
    print(f"📸 Testing image: {image_path}")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Check for Gemini API key
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_key:
        print("⚠️  Warning: GEMINI_API_KEY not set. Some features will use fallback methods.")
    else:
        print(f"✅ GEMINI_API_KEY found: {gemini_key[:10]}...")
    
    # Initialize settings
    config = Settings(
        DEVICE='cpu',  # Use CPU for local testing
        GEMINI_API_KEY=gemini_key
    )
    
    print(f"\n🔧 Configuration:")
    print(f"   Device: {config.DEVICE}")
    print(f"   Gemini API: {'Enabled' if gemini_key else 'Disabled'}")
    print(f"   Caption Type: {config.caption_type}")
    print()
    
    # Initialize models
    print("📦 Loading models...")
    try:
        model_manager = ModelManager(config)
        print("✅ Models loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load models: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Initialize pipeline
    print("\n🚀 Initializing pipeline...")
    pipeline = NutritionVideoPipeline(model_manager, config)
    
    # Process image
    job_id = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(f"\n🔄 Processing image (Job ID: {job_id})...")
    print("=" * 80)
    
    try:
        results = pipeline.process_image(image_path, job_id)
        
        print("\n" + "=" * 80)
        print("✅ Processing completed!")
        print("=" * 80)
        
        # Print Gemini call summary
        print(f"\n📊 Gemini API Call Summary:")
        print(f"   Total calls: {gemini_call_count}")
        if gemini_calls:
            print(f"   Calls breakdown:")
            for call in gemini_calls:
                print(f"     {call['call_number']}. {call['function']} - {call['details']}")
        else:
            print("   (No Gemini calls tracked - may need to patch tracking)")
        
        # Print results summary
        print(f"\n📋 Results Summary:")
        print(f"   Job ID: {results.get('job_id', 'N/A')}")
        print(f"   Media: {results.get('media_name', 'N/A')}")
        print(f"   Type: {results.get('media_type', 'N/A')}")
        
        tracking = results.get('tracking', {})
        print(f"   Objects detected: {tracking.get('total_objects', 0)}")
        
        nutrition = results.get('nutrition', {})
        if nutrition:
            items = nutrition.get('items', [])
            print(f"   Food items: {len(items)}")
            for item in items:
                food_name = item.get('food_name', 'Unknown')
                calories = item.get('total_calories', 0)
                volume = item.get('volume_ml', 0)
                print(f"     - {food_name}: {calories:.1f} cal, {volume:.1f}ml")
            
            summary = nutrition.get('summary', {})
            if summary:
                print(f"   Total calories: {summary.get('total_calories_kcal', 0):.1f} kcal")
        
        # Save results
        output_file = Path(__file__).parent / f"test_results_{job_id}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Full results saved to: {output_file}")
        
        # Save Gemini call log
        if gemini_calls:
            call_log_file = Path(__file__).parent / f"gemini_calls_{job_id}.json"
            with open(call_log_file, 'w') as f:
                json.dump(gemini_calls, f, indent=2)
            print(f"💾 Gemini call log saved to: {call_log_file}")
        
        print(f"\n✅ Test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
