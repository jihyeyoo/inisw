import requests
import os
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

# Load environment variables
try:
    # .env 파일의 절대 경로를 지정
    dotenv_path = os.path.join(os.path.dirname(__file__), '..\\', '.env.local')
    load_dotenv(dotenv_path)
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_s3_region = os.getenv('AWS_S3_REGION')
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    mongo_uri = os.getenv("MONGODB_URI")

    if not all([aws_access_key_id, aws_secret_access_key, aws_s3_region, bucket_name, mongo_uri]):
        raise ValueError("One or more environment variables are missing.")
except Exception as e:
    print(f"Error loading environment variables: {e}")
    exit(1)

# Connect to MongoDB
try:
    client = MongoClient(mongo_uri)
    db = client["lumterior"]
    images_collection = db["images"]
except ConnectionFailure:
    print("Failed to connect to MongoDB.")
    exit(1)

# Retrieve the most recent image document
try:
    document = images_collection.find_one(sort=[('uploaded_at', -1)])
    if not document:
        print("No recent document found in MongoDB.")
        exit(1)
except PyMongoError as e:
    print(f"Failed to retrieve document from MongoDB: {e}")
    exit(1)

# Set paths using the most recent document
image_path = document.get('s3_url')
mask_path = document.get('mask_path')
reference_path = f"https://{bucket_name}.s3.{aws_s3_region}.amazonaws.com/lumterior/lamp/lamp1.png"

# Check if the retrieved paths exist in the file system (if needed)
def file_exists(path):
    return os.path.exists(path)

url_process_image = "http://127.0.0.1:8080/process_image"
data_process_image = {
    "image_path": image_path,
    "mask_path": mask_path,
    "reference_path": reference_path,
    "output_dir": "api_test_results",
    "seed": 321,
    "scale": 20
}

# Validate input file paths before making the request
for key, path in data_process_image.items():
    if "path" in key and not file_exists(path):
        print(f"Error: File not found at {path}")
        exit(1)

# Make the request to process_image
response_process = requests.post(url_process_image, json=data_process_image)
print("Process Image - Status Code:", response_process.status_code)

# Handle process_image response
if response_process.status_code == 200:
    response_data = response_process.json()
    print("Process Image - Response Body:", response_data)

    # Extract processed image path
    processed_image_path = response_data.get("processed_image_path")
    original_image_path = data_process_image["image_path"]

    if processed_image_path:
        url_generate_mask = "http://127.0.0.1:8080/generate_mask"
        data_generate_mask = {
            "processed_image_path": processed_image_path,
            "original_image_path": original_image_path
        }

        # Call /generate_mask
        response_mask = requests.post(url_generate_mask, json=data_generate_mask)
        print("Generate Mask - Status Code:", response_mask.status_code)
        try:
            print("Generate Mask - Response Body:", response_mask.json())
        except requests.exceptions.JSONDecodeError:
            print("Generate Mask - Response Body: Non-JSON response")
            print("Raw Response:", response_mask.text)
    else:
        print("Processed image path not found. Skipping mask generation.")
else:
    print("Failed to process image. Response Body:", response_process.text)
