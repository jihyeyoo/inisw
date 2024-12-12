from flask import Flask, request, jsonify
import subprocess
import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from skimage.metrics import structural_similarity as compare_ssim
from flask_cors import CORS  # CORS 처리를 위한 라이브러리 임포트

app = Flask(__name__)
CORS(app)  # 모든 도메인에서 오는 요청을 허용하도록 설정

# 출력 디렉토리가 존재하는지 확인하고 없으면 생성
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
    try:
        data = request.json
        image_path = data.get("image_path")
        mask_path = data.get("mask_path")
        reference_path = data.get("reference_path")
        output_dir = data.get("output_dir", "results")
        seed = 321
        scale = 20

        # 입력 데이터 유효성 검증
        specific_mask_path = mask_path
        if specific_mask_path:
            # 특정 마스크 처리
            pass
        
        return jsonify({"message": "Image processed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate_mask", methods=["POST"])
def generate_mask():
    try:
        data = request.json
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

        # SSIM 계산 및 차이 맵 생성
        (score, diff) = compare_ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")

        # 임계값 적용 및 플러드 필
        _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        flood_filled = thresh.copy()
        h, w = flood_filled.shape[:2]
        flood_fill_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        cv2.floodFill(flood_filled, flood_fill_mask, (0, 0), 255)
        flood_filled_inverted = cv2.bitwise_not(flood_filled)
        combined_filled = cv2.bitwise_or(thresh, flood_filled_inverted)

        # 밝기 기반 마스크 생성
        gray_imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        _, bright_mask = cv2.threshold(gray_imageA, 200, 255, cv2.THRESH_BINARY)

        # 공통 마스크 생성
        common_mask = cv2.bitwise_and(combined_filled, bright_mask)

        # 마스크 스무딩
        blurred_mask = cv2.GaussianBlur(common_mask, (51, 51), 0)

        # 출력 디렉토리 설정 및 파일 저장
        lamp_mask_dir = os.path.join(OUTPUT_DIR, "lamp_mask")
        if not os.path.exists(lamp_mask_dir):
            os.makedirs(lamp_mask_dir)
        mask_path = os.path.join(lamp_mask_dir, "common_mask.png")
        cv2.imwrite(mask_path, blurred_mask)

        return jsonify({
            "message": "Common mask generated successfully",
            "mask_path": mask_path
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to generate mask: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=8080, debug=True)
