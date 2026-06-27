"""
Test S3 Connection
"""
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

S3_BUCKET = os.environ.get("S3_BUCKET")
AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

print("=" * 60)
print("  Testing S3 Connection")
print("=" * 60)
print(f"\n📦 Bucket: {S3_BUCKET}")
print(f"🌍 Region: {AWS_REGION}")
print(f"🔑 Access Key: {AWS_ACCESS_KEY[:10]}...")
print()

try:
    # Create S3 client
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    
    print("🔍 Checking bucket contents...")
    print()
    
    # List objects in bucket
    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    
    if 'Contents' in response:
        print("✅ S3 Connection Successful!")
        print(f"\n📂 Files in bucket '{S3_BUCKET}':")
        print("-" * 60)
        
        for obj in response['Contents']:
            size_kb = obj['Size'] / 1024
            print(f"  📄 {obj['Key']:<40} ({size_kb:,.1f} KB)")
        
        # Check for required files
        print("\n🔍 Checking required files:")
        print("-" * 60)
        
        files_found = [obj['Key'] for obj in response['Contents']]
        
        required_files = {
            'models/bike_model.pkl': '✅ Found' if 'models/bike_model.pkl' in files_found else '❌ Missing',
            'dataset/bike_rental.csv': '✅ Found' if 'dataset/bike_rental.csv' in files_found else '❌ Missing'
        }
        
        for file, status in required_files.items():
            print(f"  {file:<40} {status}")
        
        print("\n" + "=" * 60)
        if all('✅' in status for status in required_files.values()):
            print("🎉 All required files are present in S3!")
        else:
            print("⚠️  Some files are missing. Please upload them.")
        print("=" * 60)
        
    else:
        print("⚠️  Bucket is empty. Please upload files to S3.")
        
except Exception as e:
    print(f"❌ S3 Connection Failed!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("  - Check if Access Key ID and Secret Key are correct")
    print("  - Verify bucket name and region")
    print("  - Ensure IAM user has S3 read permissions")
