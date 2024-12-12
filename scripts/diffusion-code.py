import requests
import os

import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Ensure files exist
def file_exists(path):
    return os.path.exists(path)

# Step 1: Call /process_image to generate images
url_process_image = "http://127.0.0.1:8080/process_image"
data_process_image = {
    "image_path": "examples/image/10_138_9.png",
    "mask_path": "examples/mask/10_138_9_m.png",
    "reference_path": "examples/reference/last1.png",
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
