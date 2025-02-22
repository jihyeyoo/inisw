# /scripts/diffusion-app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import cv2
import numpy as np
import torch.nn.functional as F
from skimage.metrics import structural_similarity as compare_ssim
import requests
from urllib.parse import urlparse
import numpy as np

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = "api_test_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_image_from_url(url, grayscale=False):
    """Directly read image from URL without saving"""
    try:
        # Read image from URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert to numpy array
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        
        # Decode image
        if grayscale:
            return cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except Exception as e:
        raise Exception(f"Failed to read image from {url}: {str(e)}")

def resize_image(image, target_height=512, target_width=512):
    return cv2.resize(image, (target_width, target_height))

# API가 실행 중임을 확인하는 루트 경로
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running"}), 200

@app.route("/process_image", methods=["POST"])
def process_image():
    try:
        data = request.json
        image_url = data.get("image_path")
        mask_url = data.get("mask_path")
        reference_url = data.get("reference_path")
        output_dir = data.get("output_dir", "results")
        seed = data.get("seed", 321)
        scale = data.get("scale", 20)

        if not all([image_url, mask_url, reference_url]):
            return jsonify({"error": "Missing required URLs"}), 400

        try:
            # Read images directly from URLs
            img = read_image_from_url(image_url)
            mask = read_image_from_url(mask_url, grayscale=True)
            reference = read_image_from_url(reference_url)

            if any(x is None for x in [img, mask, reference]):
                raise Exception("Failed to load one or more images from URLs")

            # Resize images if necessary
            if img.shape[:2] != (512, 512):
                img = resize_image(img)
            if mask.shape[:2] != (512, 512):
                mask = resize_image(mask)
            if reference.shape[:2] != (512, 512):
                reference = resize_image(reference)

            # Create unique filenames using URL
            base_name = os.path.splitext(os.path.basename(urlparse(image_url).path))[0]
            if not base_name:
                base_name = 'image'

            # Save processed images temporarily for the diffusion model
            os.makedirs(output_dir, exist_ok=True)
            temp_paths = {
                'image': os.path.join(output_dir, f"{base_name}_temp.png"),
                'mask': os.path.join(output_dir, f"{base_name}_mask_temp.png"),
                'reference': os.path.join(output_dir, f"{base_name}_reference_temp.png")
            }

            for path, img_data in zip(temp_paths.values(), [img, mask, reference]):
                cv2.imwrite(path, img_data)

            # Run diffusion model
            command = [
                "python", "diffusion/scripts/inference.py",
                "--plms",
                "--outdir", output_dir,
                "--config", "diffusion/configs/v1.yaml",
                "--ckpt", "diffusion/checkpoints/model.ckpt",
                "--image_path", temp_paths['image'],
                "--mask_path", temp_paths['mask'],
                "--reference_path", temp_paths['reference'],
                "--seed", str(seed),
                "--scale", str(scale),
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"Diffusion model failed: {result.stderr}")

            processed_file_path = os.path.join(output_dir, f"{base_name}_{seed}.png")
            if not os.path.exists(processed_file_path):
                raise Exception("Processed file not found")

            # Clean up temporary files
            for temp_path in temp_paths.values():
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            return jsonify({
                "message": "Image processed successfully",
                "processed_image_path": processed_file_path,
                "output": result.stdout
            }), 200

        except Exception as e:
            raise Exception(f"Processing failed: {str(e)}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate_mask", methods=["POST"])
def generate_mask():
    try:
        data = request.json
        processed_image_url = data.get("processed_image_path")
        original_image_url = data.get("original_image_path")

        if not all([processed_image_url, original_image_url]):
            return jsonify({"error": "Missing required URLs"}), 400

        try:
            # Read images directly from URLs
            processed_img = read_image_from_url(processed_image_url)
            original_img = read_image_from_url(original_image_url)

            if any(img is None for img in [processed_img, original_img]):
                raise Exception("Failed to load images from URLs")

            # Convert to grayscale
            gray_processed = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
            gray_original = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

            # Calculate SSIM
            (score, diff) = compare_ssim(gray_processed, gray_original, full=True)
            diff = (diff * 255).astype("uint8")

            # Generate mask
            _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
            
            # Apply flood fill
            mask = np.zeros((thresh.shape[0] + 2, thresh.shape[1] + 2), dtype=np.uint8)
            flood_fill = thresh.copy()
            cv2.floodFill(flood_fill, mask, (0, 0), 255)
            flood_fill_inv = cv2.bitwise_not(flood_fill)
            
            # Combine masks
            final_mask = cv2.bitwise_or(thresh, flood_fill_inv)
            
            # Apply Gaussian blur
            final_mask = cv2.GaussianBlur(final_mask, (51, 51), 0)

            # Save mask
            mask_filename = f"mask_{os.path.basename(urlparse(processed_image_url).path)}"
            mask_path = os.path.join(OUTPUT_DIR, mask_filename)
            cv2.imwrite(mask_path, final_mask)

            return jsonify({
                "message": "Mask generated successfully",
                "mask_path": mask_path
            }), 200

        except Exception as e:
            raise Exception(f"Mask generation failed: {str(e)}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
