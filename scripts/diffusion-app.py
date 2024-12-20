from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import cv2
import numpy as np
import torch.nn.functional as F
from skimage.metrics import structural_similarity as compare_ssim

app = Flask(__name__)
CORS(app)  # CORS 설정

# Ensure the output directory exists
OUTPUT_DIR = "api_test_results"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 텐서를 목표 크기로 조정하는 함수
def resize_tensor(tensor, target_height, target_width):
    return F.interpolate(tensor, size=(target_height, target_width), mode='bilinear', align_corners=False)

# 필요 시 이미지를 512x512로 조정하는 함수
def resize_image(image, target_height=512, target_width=512):
    return cv2.resize(image, (target_width, target_height))

# API가 실행 중임을 확인하는 루트 경로
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running"}), 200

@app.route("/process_image", methods=["POST"])
def process_image():
    """
    Process an image by running an external script with specified parameters.
    """
    try:
        # Parse incoming JSON data
        data = request.json
        image_path = data.get("image_path")
        mask_path = data.get("mask_path")
        reference_path = data.get("reference_path")
        output_dir = data.get("output_dir", "results")
        seed = 321
        scale = 20

        # Validate required inputs
        if not all([image_path, mask_path, reference_path]):
            return jsonify({"error": "Missing required fields: image_path, mask_path, or reference_path"}), 400

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Load the images
        img = cv2.imread(image_path)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        reference = cv2.imread(reference_path)

        if img is None or mask is None or reference is None:
            return jsonify({"error": "Failed to load one or more images"}), 400

        # Resize images to 512x512 if necessary
        if img.shape[:2] != (512, 512):
            img = resize_image(img)
        if mask.shape[:2] != (512, 512):
            mask = resize_image(mask)
        if reference.shape[:2] != (512, 512):
            reference = resize_image(reference)

        # Save the resized images to maintain the original file naming
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        resized_image_path = os.path.join(output_dir, f"{base_name}.png")
        resized_mask_path = os.path.join(output_dir, f"{base_name}_mask_512.png")
        resized_reference_path = os.path.join(output_dir, f"{base_name}_reference_512.png")
        cv2.imwrite(resized_image_path, img)
        cv2.imwrite(resized_mask_path, mask)
        cv2.imwrite(resized_reference_path, reference)

        # Run the external script for image processing
        command = [
            "python", "diffusion/scripts/inference.py",
            "--plms",
            "--outdir", output_dir,
            "--config", "diffusion/configs/v1.yaml",
            "--ckpt", "diffusion/checkpoints/model.ckpt",
            "--image_path", resized_image_path,
            "--mask_path", resized_mask_path,
            "--reference_path", resized_reference_path,
            "--seed", str(seed),
            "--scale", str(scale),
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        # Locate the processed file in the output directory
        processed_file_name = f"{base_name}_{seed}.png"
        processed_file_path = os.path.join('C:/Paint-by-Example-main/api_test_results/results', processed_file_name)
        if not os.path.exists(processed_file_path):
            return jsonify({"error": f"Processed file not found: {processed_file_path}"}), 500

        return jsonify({
            "message": "Image processed successfully",
            "processed_image_path": processed_file_path,
            "output": result.stdout,
            "output_dir": output_dir
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate_mask", methods=["POST"])
def generate_mask():
    """
    Generates a common mask based on image comparison and brightness threshold.
    """
    try:
        data = request.json

        # Validate input
        required_fields = ["processed_image_path", "original_image_path"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        processed_image_path = data["processed_image_path"]
        original_image_path = data["original_image_path"]

        # 이미지 로딩 및 그레이스케일 변환
        imageA = cv2.imread(processed_image_path)
        imageB = cv2.imread(original_image_path)

        if imageA is None or imageB is None:
            return jsonify({"error": "Failed to load one or more images"}), 400

        # Convert images to grayscale
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        # Compute SSIM and difference
        (score, diff) = compare_ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")

        # Threshold and Flood Fill
        _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        flood_filled = thresh.copy()
        h, w = flood_filled.shape[:2]
        flood_fill_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        cv2.floodFill(flood_filled, flood_fill_mask, (0, 0), 255)
        flood_filled_inverted = cv2.bitwise_not(flood_filled)
        combined_filled = cv2.bitwise_or(thresh, flood_filled_inverted)

        # Brightness-based mask
        gray_imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        _, bright_mask = cv2.threshold(gray_imageA, 200, 255, cv2.THRESH_BINARY)

        # Generate common mask
        common_mask = cv2.bitwise_and(combined_filled, bright_mask)

        # Smooth the mask with Gaussian Blur
        blurred_mask = cv2.GaussianBlur(common_mask, (51, 51), 0)

        # Save the mask image
        mask_path = os.path.join(OUTPUT_DIR, "common_mask.png")
        cv2.imwrite(mask_path, blurred_mask)

        return jsonify({
            "message": "Common mask generated successfully",
            "mask_path": mask_path
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to generate mask: {str(e)}"}), 500

if __name__ == "__main__":
    # Run the Flask app
    app.run(port=8080,debug=True)
