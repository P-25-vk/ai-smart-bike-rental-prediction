"""
Upload Model and Dataset to AWS S3
Reads credentials from .env file
"""

import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

S3_BUCKET = os.environ.get("S3_BUCKET", "")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

def upload_to_s3():
    """Upload model and dataset to S3"""
    
    if not S3_BUCKET:
        print("❌ S3_BUCKET not configured in .env file")
        return False
    
    if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
        print("❌ AWS credentials not configured in .env file")
        return False
    
    try:
        # Create S3 client
        s3 = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        
        print(f"📦 Connecting to S3 bucket: {S3_BUCKET}")
        
        # Files to upload
        files = [
            ("bike_model.pkl", "models/bike_model.pkl"),
            ("bike_rental.csv", "dataset/bike_rental.csv"),
        ]
        
        for local_file, s3_key in files:
            if not os.path.exists(local_file):
                print(f"⚠️  {local_file} not found locally, skipping...")
                continue
            
            print(f"⬆️  Uploading {local_file} to s3://{S3_BUCKET}/{s3_key}")
            s3.upload_file(local_file, S3_BUCKET, s3_key)
            print(f"✅ Uploaded: {s3_key}")
        
        print("\n🎉 All files uploaded successfully!")
        print(f"\nS3 Structure:")
        print(f"  s3://{S3_BUCKET}/")
        print(f"  ├── models/")
        print(f"  │   └── bike_model.pkl")
        print(f"  └── dataset/")
        print(f"      └── bike_rental.csv")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  AWS S3 Upload Script - Bike Rental Prediction")
    print("=" * 60)
    print()
    upload_to_s3()
