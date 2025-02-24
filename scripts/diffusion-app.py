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
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# 상대 경로를 사용하여 .env.local 파일 경로 설정
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_s3_region = os.getenv('AWS_S3_REGION')
bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

# 환경 변수 로드 확인
print(f"AWS S3 Region: {aws_s3_region}")
print(f"Bucket Name: {bucket_name}")
print(f"AWS Access Key ID 존재: {'있음' if aws_access_key_id else '없음'}")
print(f"AWS Secret Access Key 존재: {'있음' if aws_secret_access_key else '없음'}")

# S3 클라이언트 초기화
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_s3_region
)

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

def get_s3_key_prefix(image_url):
    """S3에 업로드할 때 사용할 키 프리픽스 생성 함수"""
    # URL에서 파일명 추출 (예: 10_449_4.png)
    file_name = os.path.basename(urlparse(image_url).path)
    
    # S3 키 프리픽스 생성 (예: 10_449_4.png-diffusion-results/)
    return f"results/{file_name}-diffusion-results/"

def upload_file_to_s3(local_path, s3_key, content_type="image/png"):
    """로컬 파일을 S3에 업로드하는 함수"""
    try:
        s3_client.upload_file(
            local_path, 
            bucket_name, 
            s3_key,
            ExtraArgs={'ContentType': content_type}
        )
        return f"https://{bucket_name}.s3.{aws_s3_region}.amazonaws.com/{s3_key}"
    except NoCredentialsError:
        raise Exception("AWS 자격 증명이 없거나 잘못되었습니다.")
    except ClientError as e:
        raise Exception(f"S3 업로드 중 오류 발생: {str(e)}")
    except Exception as e:
        raise Exception(f"파일 업로드 실패: {str(e)}")

def upload_directory_to_s3(local_dir, s3_prefix):
    """디렉토리 전체를 S3에 업로드하는 함수"""
    s3_urls = {}
    
    try:
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                
                # 로컬 경로에서 상대 경로 추출
                relative_path = os.path.relpath(local_path, start=local_dir)
                
                # 상대 경로가 None이나 빈 문자열이 아닌지 확인
                if not relative_path:
                    print(f"Warning: Empty relative path for {local_path}")
                    continue
                
                # 윈도우 경로 구분자를 URL 경로 구분자로 변환
                relative_path_fixed = relative_path.replace('\\', '/')
                
                # S3 키 생성
                s3_key = f"{s3_prefix}{relative_path_fixed}"
                
                # 파일이 실제로 존재하는지 확인
                if not os.path.exists(local_path):
                    print(f"Warning: File does not exist: {local_path}")
                    continue
                
                # 콘텐츠 타입 결정
                content_type = "image/png" if file.endswith(".png") else "application/octet-stream"
                
                # S3에 업로드
                try:
                    s3_client.upload_file(
                        local_path, 
                        bucket_name, 
                        s3_key,
                        ExtraArgs={'ContentType': content_type}
                    )
                    s3_url = f"https://{bucket_name}.s3.{aws_s3_region}.amazonaws.com/{s3_key}"
                    s3_urls[relative_path_fixed] = s3_url
                    print(f"파일 업로드 완료: {local_path} -> {s3_url}")
                except Exception as e:
                    print(f"개별 파일 업로드 실패: {local_path} -> {str(e)}")
                    continue
                
        return s3_urls
    except Exception as e:
        print(f"디렉토리 업로드 세부 오류: {str(e)}")
        raise Exception(f"디렉토리 업로드 실패: {str(e)}")

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
        print(f"Processing image: {image_url}, mask: {mask_url}, reference: {reference_url}")

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
                    
            # S3에 결과 업로드
            s3_prefix = get_s3_key_prefix(image_url)
            
            # output_dir만 S3에 업로드
            print(f"S3 업로드 시작: {output_dir} -> {s3_prefix}")
            s3_urls = upload_directory_to_s3(output_dir, s3_prefix)

            # 결과 이미지의 S3 URL 계산
            relative_path = os.path.relpath(processed_file_path, start=output_dir)
            relative_path_fixed = relative_path.replace('\\', '/')
            s3_processed_image_path = f"https://{bucket_name}.s3.{aws_s3_region}.amazonaws.com/{s3_prefix}{relative_path_fixed}"
            
            print(f"S3 업로드 완료. 결과 이미지: {s3_processed_image_path}")
        except Exception as e:
            print(f"S3 업로드 중 오류 발생: {str(e)}")
            return jsonify({"error": f"Image processing failed: {str(e)}"}), 500

        return (
            jsonify(
                {
                    "message": "Image processed successfully",
                    "processed_image_path": processed_file_path,
                    "s3_processed_image_path": s3_processed_image_path,
                    "original_image_path": image_url,
                    "reference_path": reference_url,
                    "output": result.stdout,
                    "s3_urls": s3_urls
                }
            ),
            200,
        )

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
        image_url = data.get("original_image_path")  # 원본 이미지 URL

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
        
        # S3에 마스크 업로드 코드 수정
        filename = image_url.split('-')[-1]  # 하이픈으로 분리한 후 마지막 부분을 추출
        s3_prefix = get_s3_key_prefix(filename)
        parent_dir = os.path.dirname(output_dir)
        relative_path = os.path.relpath(mask_path, start=parent_dir)
        relative_path_fixed = relative_path.replace('\\', '/')
        s3_key = f"{s3_prefix}{relative_path_fixed}"

        # S3에 업로드
        s3_mask_url = upload_file_to_s3(mask_path, s3_key, "image/png")

        return jsonify({
            "message": "Common mask generated successfully",
            "mask_path": mask_path,
            "s3_mask_url": s3_mask_url
        }), 200

    except Exception as e:
        print(f"Error in generate_mask: {str(e)}")  # 오류 로그 추가
        return jsonify({"error": f"Failed to generate mask: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)