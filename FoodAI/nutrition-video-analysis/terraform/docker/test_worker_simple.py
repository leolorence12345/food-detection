#!/usr/bin/env python3
"""
Simple test script for worker.py - can run with or without Docker
Just needs the dependencies installed and a test image
"""
import os
import sys
import json
from pathlib import Path

# Set up environment variables
os.environ['S3_VIDEOS_BUCKET'] = 'mock-bucket'
os.environ['S3_RESULTS_BUCKET'] = 'mock-results-bucket'
os.environ['S3_MODELS_BUCKET'] = 'mock-models-bucket'  # Set to empty to skip model downloads
os.environ['DYNAMODB_JOBS_TABLE'] = 'mock-jobs-table'
os.environ['SQS_VIDEO_QUEUE_URL'] = 'mock-queue-url'
os.environ['DEVICE'] = os.environ.get('DEVICE', 'cpu')
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', '')
os.environ['MAX_FRAMES'] = '60'
os.environ['FRAME_SKIP'] = '10'
os.environ['DETECTION_INTERVAL'] = '30'

# Determine if we're in Docker or local
IN_DOCKER = os.path.exists('/app/worker.py')
if IN_DOCKER:
    sys.path.insert(0, '/app')
    APP_DIR = '/app'
else:
    # Local execution - adjust paths
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    APP_DIR = str(script_dir)
    # Set app directory in environment for model paths
    os.environ['APP_DIR'] = APP_DIR

print(f"📍 Running {'in Docker' if IN_DOCKER else 'locally'} from {APP_DIR}")

# Mock AWS services
class MockS3:
    def download_file(self, bucket, key, local_path):
        print(f"📥 [Mock S3] Would download s3://{bucket}/{key} to {local_path}")
    
    def put_object(self, **kwargs):
        print(f"📤 [Mock S3] Would upload to s3://{kwargs.get('Bucket')}/{kwargs.get('Key')}")

class MockSQS:
    def receive_message(self, **kwargs):
        return {'Messages': []}
    def delete_message(self, **kwargs):
        pass

class MockDynamoDB:
    class Table:
        def __init__(self, name):
            self.name = name
        def update_item(self, **kwargs):
            pass

class MockBoto3:
    def client(self, service, **kwargs):
        if service == 's3':
            return MockS3()
        elif service == 'sqs':
            return MockSQS()
        return None
    def resource(self, service, **kwargs):
        if service == 'dynamodb':
            return MockDynamoDB()
        return None

# Mock boto3 before importing worker
sys.modules['boto3'] = MockBoto3()

# Import worker
try:
    import worker
except ImportError as e:
    print(f"❌ Error importing worker: {e}")
    print("\n💡 To run without Docker, you need to install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n   Or use Docker:")
    print("   docker build -t nutrition-worker .")
    print("   docker run -v $(pwd):/app nutrition-worker python3 test_worker_simple.py <image>")
    sys.exit(1)

# Mock AWS functions
def mock_update_job_status(job_id: str, status: str, **kwargs):
    print(f"📊 [Mock] Job {job_id}: {status}")

def mock_upload_results(job_id: str, results: dict):
    output_dir = Path(APP_DIR) / 'test_results'
    output_dir.mkdir(exist_ok=True)
    results_file = output_dir / f'{job_id}_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"💾 Results saved to: {results_file}")
    return f'results/{job_id}/results.json'

worker.update_job_status = mock_update_job_status
worker.upload_results = mock_upload_results

# Skip model downloads if S3_MODELS_BUCKET is mock
if os.environ.get('S3_MODELS_BUCKET') == 'mock-models-bucket':
    worker.download_models_from_s3 = lambda: print("⏭️  Skipping model downloads (using mock bucket)")

def test_image(image_path: str):
    """Test processing a single image"""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    import uuid
    job_id = f"test-{uuid.uuid4().hex[:8]}"
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing worker.py")
    print(f"{'='*60}")
    print(f"📝 Job ID: {job_id}")
    print(f"🖼️  Image: {image_path}")
    print(f"💻 Device: {os.environ.get('DEVICE', 'cpu')}")
    print(f"{'='*60}\n")
    
    try:
        print("🚀 Starting processing...")
        results = worker.process_media(image_path, job_id)
        
        print(f"\n{'='*60}")
        print("✅ Processing completed!")
        print(f"{'='*60}\n")
        
        print("📊 Results:")
        print(f"  Media Type: {results.get('media_type')}")
        print(f"  Detected Items: {len(results.get('detected_items', []))}")
        
        if results.get('detected_items'):
            print("\n  Food Items:")
            for i, item in enumerate(results.get('detected_items', []), 1):
                name = item.get('name', 'Unknown')
                calories = item.get('calories', 'N/A')
                print(f"    {i}. {name} - {calories} cal")
        
        meal_summary = results.get('meal_summary', {})
        if meal_summary:
            print(f"\n  Total Calories: {meal_summary.get('total_calories', 'N/A')}")
        
        mock_upload_results(job_id, results)
        return results
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_worker_simple.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = test_image(image_path)
    sys.exit(0 if result else 1)


