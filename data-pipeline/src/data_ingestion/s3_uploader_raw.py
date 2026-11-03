
import os
import boto3
from pathlib import Path
from dotenv import load_dotenv

def upload_data_to_s3():
    """Upload data from data/raw/ to S3 bucket"""
    
    print("Starting data upload to S3...")
    
    # Load environment variables
    load_dotenv()
    
    # Get AWS credentials from .env file
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    if not bucket_name:
        print("ERROR: AWS_S3_BUCKET_NAME not found in .env file!")
        return False
    
    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    
    try:
        # Create S3 client
        s3 = boto3.client('s3', region_name=region)
        
        # Create bucket if it doesn't exist
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' exists")
        except:
            print(f"Creating bucket '{bucket_name}'...")
            if region == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            print(f"Bucket created!")

        
        # Find CSV files in data/raw/
        data_folder = Path("data/raw")

        if not data_folder.exists():
            data_folder = Path("../../data/raw")

        if not data_folder.exists():
            print(f"ERROR: Data folder '{data_folder}' does not exist!")
            print("Make sure you have the data/raw with CSV files")
            return False

 

        # Get list of CSV files
        csv_files = list(data_folder.glob("*.csv"))

        if not csv_files:
            print(f"No CSV files found in '{data_folder}'")
            return False
        print(f"Found {len(csv_files)} CSV files in '{data_folder}'")

        # Upload each file
        uploaded_count = 0
        for csv_file in csv_files:
            s3_key = f"raw-data/{csv_file.name}"
            print(f"Uploading {csv_file} to s3://{bucket_name}/{s3_key}...")

            try:
                    s3.upload_file(str(csv_file), bucket_name, s3_key)
                    print(f"Uploaded {csv_file.name} to S3")
                    uploaded_count += 1
            except Exception as upload_error:
                    print(f"ERROR: Failed to upload {csv_file.name} to S3: {e}")
 
        if uploaded_count == len(csv_files):
            print(f"Successfully uploaded all {uploaded_count} files to S3!")
            return True
        else:
            print(f"Partially uploaded {uploaded_count} out of {len(csv_files)} files to S3.")
            return False

    except Exception as e:
        print(f"ERROR: Failed to upload data to S3: {e}")
        print("Check your AWS credentials and bucket permissions.")
        return False

    
# Verification
def verify_upload():
    """Verify if the uploaded files exist in S3 bucket"""
    
    print("Verifying uploaded files in S3...")
    
    # Load environment variables
    load_dotenv()
    
    # Get AWS credentials from .env file
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    if not bucket_name:
        print("ERROR: AWS_S3_BUCKET_NAME not found in .env file!")
        return
    
    try:
        # Create S3 client
        s3 = boto3.client('s3', region_name=region)
        
        # List objects in the bucket under raw-data/
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='raw-data/')
        
        if "Contents" in response:
            print(f"Uploaded files in S3 bucket '{bucket_name}':")
            files = response['Contents']
            total_size_mb = 0 
            for file in files:
                size_mb = file['Size'] / (1024 * 1024)  # Convert bytes to MB
                total_size_mb += size_mb
                print(f"- {file['Key']} (Size: {size_mb:.2f} MB)")
            print(f"Total size of uploaded files: {total_size_mb:.2f} MB")
            print("Upload verification completed successfully!")
            return True
        else:
            print(f"No files found in S3 bucket '{bucket_name}' under 'raw-data/'")
            return False 
    
    except Exception as e:
        print(f"ERROR: Failed to verify upload in S3: {e}")
        return False

if __name__ == "__main__":
    # Run upload
    success = upload_data_to_s3()
    
    # Verify if upload was successful
    if success:
        verify_upload()
    
    print("\nNext step: Data processing and transformation!")
