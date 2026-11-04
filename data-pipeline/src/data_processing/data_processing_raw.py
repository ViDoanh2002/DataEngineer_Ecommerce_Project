"""
TUTORIAL: Data Processing Pipeline
Download data from S3, clean it, transform it, and upload results back to S3.
"""

import os
import boto3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import tempfile

def process_ecommerce_data():
    """Download, process, and upload e-commerce data"""
    
    print("Starting data processing...")
    
    # Load environment variables
    load_dotenv()
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    if not bucket_name:
        print("ERROR: AWS_S3_BUCKET_NAME not found in .env file!")
        return False
    
    print(f"Processing data from bucket: {bucket_name}")
    
    try:
        # Create S3 client
        s3 = boto3.client('s3',region_name=region)
        
        # Step 1: Download data from S3
        print("\nStep 1: Downloading data from S3...")
        datasets = download_data_from_s3(s3, bucket_name)
        print(datasets)
        
        # Step 2: Clean and transform data
        print("\nStep 2: Cleaning and transforming data...")
        #processed_datasets = transform_data(datasets)
        
        # Step 3: Create business metrics
        print("\nStep 3: Creating business metrics...")
        #business_metrics = create_business_metrics(processed_datasets)
        
        # Step 4: Upload processed data back to S3
        print("\nStep 4: Uploading processed data to S3...")
        #upload_success = upload_processed_data(s3, bucket_name, processed_datasets, business_metrics)
        
        #if upload_success:
        #    print("\nSUCCESS: Data processing pipeline completed!")
        #    return True
        #else:
        #    print("\nERROR: Failed to upload processed data")
        #    return False
            
    except Exception as e:
        print(f"ERROR: Data processing failed: {e}")
        return False

def download_data_from_s3(s3, bucket_name):
    """Download CSV files from S3 bucket and return as pandas DataFrames"""
    datasets = {}
    # List objects in the bucket
    data_files = ['customer.csv', 'orders.csv', 'products.csv', 'oder_items.csv', 'reviews.csv']
    for file_name in data_files: 
        try: 
            print(f"Downloading {file_name}...")

            s3_key = f"raw-data/{file_name}"
            local_path = os.path.join(tempfile.gettempdir(), file_name)

            s3.download_file(bucket_name, s3_key, local_path)

            df = pd.read_csv(local_path)
            dataset_name = file_name.replace('.csv', '')
            datasets[dataset_name] = df

            print(f"Load {dataset_name} dataset with {len(df)} records")

            os.remove(local_path)  # Clean up the temporary file
        except Exception as e:
            print(f"ERROR: Failed to download {file_name} from S3: {e}")
            continue
    return datasets

def transform_data(datasets):
    processed = {}

    # Processed customer data
    if 'customer' in datasets: 
        customer = datasets['customer'].copy()
        # Clean email addresses
        customer['email'] = customer['email'].str.lower().str.strip()

        # Convert date 
        customer['date_of_birth'] = pd.to_datetime(customer['date_of_birth'])
        customer['registration_date'] = pd.to_datetime(customer['registration_date'])

        # Calculate age
        customer['age'] = (datetime.now() - customer['date_of_birth']).dt.days // 365 

        # Create age groups 
        customer['age_group'] = pd.cut(customer['age'], bins=[0,25,35,50,65,100], labels=['18-25','26-35','36-50','51-65','65+'])

        processed['customer'] = customer 

        print(f'Processed customer: {len(customer)} records')

    # Processed product data
    if 'product' in datasets:
        product = datasets['product'].copy()
        # Clean product names
        product['product_name'] = product['product_name'].str.strip()

        # Convert price to numeric 
        product['price'] = pd.to_numeric(product['price'], errors = 'coerce')

        # Create price categories  
        product['price_category'] = pd.cut(product['price'], bins=[0,50,150,500,float('inf')], labels=['Budget','Mid-range','Premium','Luxury'])

        processed['product_clean'] = product 

        print(f'Processed product: {len(product)} records')

    # Processed orders data 
    if 'orders' in datasets:
        orders = datasets['orders'].copy()
        # Convert date 
        orders['order_date'] = pd.to_datetime(orders['order_date'])

        # Convert total amount to numeric
        orders['total_amount'] = pd.to_numeric(orders['total_amount'], errors = 'coerce')

        # Extract month and year for seasonal analysis
        orders['order_month'] = orders['order_date'].dt.month
        orders['order_year'] = orders['order_date'].dt.year

        processed['orders_clean'] = orders 

        print(f'Processed orders: {len(orders)} records')        

     # Processed order item data
    if 'order_items' in datasets:
        order_items = datasets['order_items'].copy()

        # Convert total amount to numeric
        order_items['quantity'] = pd.to_numeric(order_items['quantity'], errors = 'coerce')
        order_items['unit_price'] = pd.to_numeric(order_items['unit_price'], errors = 'coerce')

        # Calculate total price per item
        order_items['total_price'] = order_items['quantity'] * order_items['unit_price']

        processed['order_items_clean'] = order_items

        print(f'Processed order items: {len(order_items)} records')

    # Processed reviews data 
    if 'reviews' in datasets:
        reviews = datasets['reviews'].copy()
        # Convert date 
        reviews['review_date'] = pd.to_datetime(reviews['review_date'])

        # Convert rating to numeric
        reviews['rating'] = pd.to_numeric(reviews['rating'], errors = 'coerce')

        # Create rating categories
        reviews['rating_category'] = reviews['rating'].apply(
            lambda x: 'Excellent' if x >= 4.5 else 'Good' if x >= 3 else 'Average' if x >= 2.5 else 'Poor'
        )

        processed['reviews_clean'] = reviews

        print(f'Processed reviews: {len(reviews)} records')

    return processed

if __name__ == "__main__":
    #TODO: Call process_ecommerce_data() and handle the results
    process_ecommerce_data()
    pass
