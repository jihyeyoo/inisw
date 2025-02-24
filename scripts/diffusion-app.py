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

def get_output_dir_from_image(reference_url, base_dir="."):
    """입력 이미지 파일명(lampX.png)에 맞는 lampX_results 폴더를 찾는 함수"""
    # URL에서 파일명(lampX.png) 추출
    base_name = os.path.splitext(os.path.basename(urlparse(reference_url).path))[0]  # lampX 추출
    output_dir = os.path.join(base_dir, f"{base_name}_results")
    os.makedirs(output_dir, exist_ok=True)

    # 결과 폴더가 존재하는지 확인
    if os.path.exists(output_dir):
        return output_dir
    else:
        raise Exception(f"Output directory not found: {output_dir}")

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


@app.route("/process_image", methods=["POST"])
def process_image():
    data = request.json

    # Initialize URLs
    image_url = None
    mask_url = None
    reference_url = None
    seed = data.get("seed", 321)
    scale = data.get("scale", 20)

    try:
        # Extract URLs from request
        image_url = data.get("image_path")
        mask_url = data.get("mask_path")
        reference_url = data.get("reference_path")

        # 최신 output 디렉토리 다시 설정
        output_dir = get_output_dir_from_image(reference_url)

        # Debugging logs
        print(
            f"Processing image: {image_url}, mask: {mask_url}, reference: {reference_url}"
        )

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
                base_name = "image"

            # Save processed images temporarily for the diffusion model
            os.makedirs(output_dir, exist_ok=True)
            temp_paths = {
                "image": os.path.join(output_dir, f"{base_name}_temp.png"),
                "mask": os.path.join(output_dir, f"{base_name}_mask_temp.png"),
                "reference": os.path.join(
                    output_dir, f"{base_name}_reference_temp.png"
                ),
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

            # Log command output
            print(f"Command output: {result.stdout}")
            print(f"Command error output: {result.stderr}")
            print(f"Return code: {result.returncode}")

            if result.returncode != 0:
                print(f"Diffusion model stderr: {result.stderr}")  # 오류 메시지 출력
                raise Exception(f"Diffusion model failed: {result.stderr}")

            processed_file_path = os.path.join(output_dir, "results", f"{base_name}_temp_{seed}.png")
            # print(processed_file_path);
            if not os.path.exists(processed_file_path):
                raise Exception("Processed file not found")
            
            # Clean up temporary files
            for temp_path in temp_paths.values():
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            return (
                jsonify(
                    {
                        "message": "Image processed successfully",
                        "processed_image_path": processed_file_path,
                        "original_image_path": image_url,
                        "reference_path":reference_url,
                        "output": result.stdout,
                    }
                ),
                200,
            )

        except Exception as e:
            raise Exception(f"Processing failed: {str(e)}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # 오류 메시지 출력
        return jsonify({"error": str(e)}), 500


@app.route("/generate_mask", methods=["POST"])
def generate_mask():
    data = request.json

    try:
        processed_image_path = data.get("processed_image_path")  # 조명 합성된 후 이미지
        original_image_path = data.get("original_image_path")  # 조명 합성되기 전 이미지
        reference_url = data.get("reference_path")  # 참고 이미지 URL

        # 디버깅 로그 추가
        print(f"Processed Image Path: {processed_image_path}")
        print(f"Original Image Path: {original_image_path}")
        print(f"Reference URL: {reference_url}")

        if not all([processed_image_path, original_image_path, reference_url]):
            return jsonify({"error": "Missing required parameters"}), 400

        # 최신 output 디렉토리 설정
        try:
            output_dir = get_output_dir_from_image(reference_url)
            print(f"Using Output Directory: {output_dir}")  # 디버깅 로그 추가
        except Exception as e:
            return jsonify({"error": f"Failed to get output directory: {str(e)}"}), 500

        # 이미지 로드
        imageA = cv2.imread(processed_image_path)  # 조명 합성된 이미지
        imageB = read_image_from_url(original_image_path)  # 원본 이미지 (URL에서 직접 로드)

        if imageA is None or imageB is None:
            return jsonify({"error": "Failed to load one or more images"}), 400

        # 그레이스케일 변환
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        # SSIM(구조적 유사도) 비교
        (score, diff) = compare_ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")

        # 차이 영역 이진화
        _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # Flood Fill 적용
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

        # 가우시안 블러 처리
        blurred_mask = cv2.GaussianBlur(common_mask, (51, 51), 0)

        # 마스크 파일 저장
        base_name = os.path.splitext(os.path.basename(urlparse(processed_image_path).path))[0]
        mask_filename = f"mask_{base_name}.png"
        mask_path = os.path.join(output_dir, mask_filename)

        # 디버깅 로그 추가
        print(f"Saving mask to: {mask_path}")

        cv2.imwrite(mask_path, blurred_mask)

        return jsonify({
            "message": "Common mask generated successfully",
            "mask_path": mask_path
        }), 200

    except Exception as e:
        print(f"Error in generate_mask: {str(e)}")  # 오류 로그 추가
        return jsonify({"error": f"Failed to generate mask: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)