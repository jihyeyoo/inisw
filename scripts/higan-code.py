import os
import sys
import uuid
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import requests
from sklearn.cluster import DBSCAN

# 초기 환경 설정
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

os.system(f"pip install -r requirements.txt")

# Higan 저장소 클론 및 파일 설정
CODE_DIR = 'higan'
if not os.path.exists(CODE_DIR):
    os.system(f'git clone https://github.com/genforce/higan.git {CODE_DIR}')

os.chdir(CODE_DIR)

# 필요한 디렉토리 생성
pretrain_dir = 'models/pretrain/pytorch'
os.makedirs(pretrain_dir, exist_ok=True)

# 모델 및 파일 다운로드
def download_file(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    else:
        print(f"Failed to download {url}, status code: {response.status_code}")

# StyleGAN 모델 다운로드
stylegan_url = 'https://www.dropbox.com/s/h1w7ld4hsvte5zf/stylegan_bedroom256_generator.pth?dl=1'
stylegan_path = os.path.join(pretrain_dir, 'stylegan_bedroom256_generator.pth')
download_file(stylegan_url, stylegan_path)

# Order W 파일 다운로드
order_w_url = 'https://www.dropbox.com/s/hwjyclj749qtp89/order_w.npy?dl=1'
order_w_path = os.path.join(os.getcwd(), 'order_w_1k.npy')
download_file(order_w_url, order_w_path)

print("모든 파일 다운로드 완료!")

# 경로 및 모듈 설정
WORK_DIR = os.getcwd()
sys.path.append(WORK_DIR)

from models.helper import build_generator
from utils.logger import setup_logger
from utils.editor import get_layerwise_manipulation_strength, manipulate

# 모델 빌드 함수
def build_model(model_name, logger=None):
    """Builds the generator by model name."""
    model = build_generator(model_name, logger=logger)
    return model

def sample_codes(model, num, seed=0, w1k_code=None):
    """Samples latent codes randomly."""
    np.random.seed(seed)

    if w1k_code is None:
        latent_codes = model.easy_sample(num)
    else:
        latent_codes = w1k_code[np.random.randint(0, w1k_code.shape[0], num)]

    # 잠재 코드의 차원 확인 및 조정
    if latent_codes.ndim == 1:
        # 예상한 차원이 아닌 경우, 512 차원으로 확장
        latent_codes = latent_codes.reshape(1, -1)
        if latent_codes.shape[1] != 512:
            latent_codes = np.tile(latent_codes, (1, 512 // latent_codes.shape[1]))

    if latent_codes.ndim == 2 and latent_codes.shape[1] != 512:
        raise ValueError(f"Invalid latent codes shape: {latent_codes.shape}. Expected [batch_size, 512].")

    # 모델로부터 잠재 코드 변환
    latent_codes = model.easy_synthesize(
        latent_codes=latent_codes,
        latent_space_type='w',
        generate_style=False,
        generate_image=False
    )['wp']

    return latent_codes

# order_w.npy 로드
if os.path.exists(order_w_path):
    w1k_code = np.load(order_w_path)
    print("w1k_code 로드 성공!")
else:
    print("order_w_1k.npy 파일을 찾을 수 없습니다. 경로를 확인하세요.")

import torch

# Define device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Build and initialize the indoor model
indoor_model_name = "stylegan_bedroom"
indoor_model = build_model(indoor_model_name)
indoor_model.load()
indoor_model.net.to(device)
indoor_model.net.eval()

import certifi

# MongoDB 연결 및 이미지 정보 가져오기
def connect_to_mongodb():
    # 상대 경로를 사용하여 .env.local 파일의 경로를 지정
    dotenv_path = os.path.join(os.path.dirname(__file__), '..\..', '.env.local')
    load_dotenv(dotenv_path)
    print(dotenv_path)
    try:
        # 환경 변수에서 URI를 읽고 MongoClient에 연결 정보를 전달
        uri = os.getenv("MONGODB_URI")
        if uri is None:
            raise Exception("MONGODB_URI 환경 변수가 설정되지 않았습니다.")
        # CA 파일 경로를 certifi를 사용하여 가져옵니다.
        ca = certifi.where()
        client = MongoClient(uri, tlsCAFile=ca)
        db = client["lumterior"]
        print("MongoDB 연결 성공!")  # 디버깅 로그
        return db
    except Exception as e:
        print(f"MongoDB 연결 실패: {e}")  # 디버깅 로그
        sys.exit(1)

import re

def parse_image_info(db):
    try:
        # MongoDB의 "images" 컬렉션에서 가장 최근 데이터를 가져오기
        image_collection = db["images"]

        print("Debug: Fetching the most recent document...")
        recent_image = image_collection.find_one(
            sort=[("uploaded_at", -1)]  # `uploaded_at` 기준 내림차순 정렬
        )

        # 데이터가 없을 경우
        if not recent_image:
            print("Error: No documents found in the 'images' collection.")
            return None, None, None

        # 컬렉션 내 image_name 확인
        image_name = recent_image.get("image_name", "")
        if not image_name:
            print("Error: 'image_name' is missing or empty.")
            return None, None, None

        print(f"Debug: Processing image_name: {image_name}")

        # 이미지 이름에서 숫자 추출
        try:
            numbers = list(map(int, re.findall(r'\d+', image_name)))
            print(f"Debug: Extracted numbers: {numbers}")

            # 숫자 개수 검증
            if len(numbers) == 3:
                num_sample, noise_seed, image_num = numbers
                print(f"Debug: Parsed values - num_sample: {num_sample}, noise_seed: {noise_seed}, image_num: {image_num}")
                return num_sample, noise_seed, image_num
            else:
                print("Error: 'image_name' does not contain exactly 3 components.")
                return None, None, None

        except ValueError as ve:
            print(f"Error: Failed to extract numbers from 'image_name': {image_name}. Exception: {ve}")
            return None, None, None

    except Exception as e:
        print(f"Error: Exception in parse_image_info: {e}")
        return None, None, None
    
import cv2
import matplotlib.patches as patches
from models.stylegan_generator import StyleGANGenerator

# Load boundary
BOUNDARY_NAME = 'indoor_lighting_boundary.npy'
BASE_DIR = 'boundaries/stylegan_bedroom'

def load_boundary(boundary_name, base_dir):
    path = os.path.join(base_dir, boundary_name)
    boundary_file = np.load(path, allow_pickle=True).item()
    boundary = boundary_file['boundary']
    manipulate_layers = boundary_file['meta_data']['manipulate_layers']
    return boundary, manipulate_layers

boundary, manipulate_layers = load_boundary(BOUNDARY_NAME, BASE_DIR)

# Load parsed image info
mongo_db = connect_to_mongodb()
num_sample, noise_seed, image_num = parse_image_info(mongo_db)

# latent_codes 생성
indoor_latent_codes = sample_codes(indoor_model, num_sample, seed=noise_seed, w1k_code=w1k_code)
sysnthesis_kwargs = {'latent_space_type': 'wp'}
images = indoor_model.easy_synthesize(indoor_latent_codes, **sysnthesis_kwargs)['image']

attribute_name = 'indoor_lighting'
model_name = 'stylegan_bedroom'
path = f'boundaries/{model_name}/{attribute_name}_boundary.npy'

# Boundary 파일 로드
try:
    boundary_file = np.load(path, allow_pickle=True).item()  # 파일을 사전 형식으로 로드
    boundary = boundary_file['boundary']
    manipulate_layers = boundary_file['meta_data']['manipulate_layers']
except ValueError:
    # Boundary 파일이 사전 형식이 아닌 경우 처리
    boundary = np.load(path)
    if attribute_name == 'view':
        manipulate_layers = '0-4'
    else:
        manipulate_layers = '6-11'

# Strength 설정
if attribute_name == 'view':
    # View attribute에 대해 모든 레이어에 동일한 조작 강도를 설정
    strength = [1.0 for _ in range(indoor_model.num_layers)]
else:
    # 기타 attribute에 대해 조작 강도를 설정
    strength = get_layerwise_manipulation_strength(
        num_layers=indoor_model.num_layers,
        truncation_psi=indoor_model.truncation_psi,
        truncation_layers=indoor_model.truncation_layers
    )

# 조작 거리 및 결과 생성
distance = -3  # {min: -3.0, max: 3.0, step: 0.1}
indoor_codes1 = manipulate(
    latent_codes=indoor_latent_codes,
    boundary=boundary,
    start_distance=0,
    end_distance=distance,
    step=2,
    layerwise_manipulation=True,
    num_layers=indoor_model.num_layers,
    manipulate_layers=manipulate_layers,
    is_code_layerwise=True,
    is_boundary_layerwise=False,
    layerwise_manipulation_strength=strength
)

np.save('latent_codes_1.npy', indoor_codes1)  # latent space 저장

distance = 3 #{min:-3.0, max:3.0, step:0.1}
indoor_codes2 = manipulate(latent_codes=indoor_latent_codes,
                     boundary=boundary,
                     start_distance=0,
                     end_distance=distance,
                     step=2,
                     layerwise_manipulation=True,
                     num_layers=indoor_model.num_layers,
                     manipulate_layers=manipulate_layers,
                     is_code_layerwise=True,
                     is_boundary_layerwise=False,
                     layerwise_manipulation_strength=strength)

np.save('latent_codes_2.npy', indoor_codes2)  # latent space 저장

import matplotlib.patches as patches
import os
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
import cv2
from sklearn.cluster import DBSCAN
from scipy.ndimage import maximum_position

# Boundary 파일 로드 함수 정의
def load_boundary(boundary_name, base_dir='boundaries/stylegan_bedroom'):
    path = os.path.join(base_dir, boundary_name)
    try:
        boundary_file = np.load(path, allow_pickle=True).item()
        boundary = boundary_file['boundary']
        manipulate_layers = boundary_file['meta_data']['manipulate_layers']
        print(f"Boundary 로드 성공: {path}")
        return boundary, manipulate_layers
    except FileNotFoundError:
        print(f"Boundary 파일을 찾을 수 없습니다: {path}")
    except Exception as e:
        print(f"Boundary 로드 중 오류 발생: {e}")

# latent_codes 파일 로드 함수 정의
def load_latent_codes(file_name, base_dir=''):
    path = os.path.join(base_dir, file_name)
    if not os.path.exists(path):
        print(f"File not found: {path}")
    try:
        latent_codes = np.load(path)
        print(f"{file_name} loaded successfully, shape: {latent_codes.shape}")
        return latent_codes
    except Exception as e:
        print(f"Failed to load {file_name}: {e}")

# Grad-CAM 계산 함수
def calculate_grad_cam(feature_map, gradients):
    pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])  # [C]
    grad_cam = torch.zeros_like(feature_map[0, 0])
    for i in range(feature_map.shape[1]):
        grad_cam += pooled_gradients[i] * feature_map[0, i]
    grad_cam = torch.relu(grad_cam)  # ReLU 적용
    grad_cam -= grad_cam.min()  # 정규화
    grad_cam /= grad_cam.max()
    return grad_cam.detach().cpu().numpy()

# Heatmap을 원본 이미지에 겹쳐서 시각화하는 함수
def overlay_heatmap_on_image(image, grad_cam, alpha=0.5, cmap='jet'):
    grad_cam_resized = cv2.resize(grad_cam, (image.shape[1], image.shape[0]))
    heatmap = cv2.applyColorMap(np.uint8(grad_cam_resized * 255), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    if image.max() > 1:
        image = image / 255.0
    overlayed_image = alpha * heatmap / 255.0 + (1 - alpha) * image
    overlayed_image = np.clip(overlayed_image, 0, 1)
    return overlayed_image

# Heatmap 클러스터링 함수 (DBSCAN 활용)
def cluster_heatmap_with_dbscan(heatmap, eps=3, min_samples=5, prob_threshold=0.5):
    high_prob_indices = np.argwhere(heatmap >= prob_threshold)
    high_prob_values = heatmap[heatmap >= prob_threshold]

    db = DBSCAN(eps=eps, min_samples=min_samples).fit(high_prob_indices)
    labels = db.labels_

    clusters = {}
    for cluster_id in set(labels):
        if cluster_id == -1:  # Noise 처리
            continue
        cluster_points = high_prob_indices[labels == cluster_id]
        cluster_values = high_prob_values[labels == cluster_id]
        clusters[cluster_id] = (cluster_points, cluster_values)

    return clusters

# Load latent codes and boundary
boundary, manipulate_layers = load_boundary('indoor_lighting_boundary.npy')
latent_codes1 = load_latent_codes('latent_codes_1.npy')
latent_codes2 = load_latent_codes('latent_codes_2.npy')

# Generator 모델 로드
from models.stylegan_generator import StyleGANGenerator
from models.model_settings import MODEL_POOL

model_name = 'stylegan_bedroom'
generator = StyleGANGenerator(model_name=model_name)
generator.weight_path = MODEL_POOL[model_name]['weight_path']
generator.load()
generator.net.eval()

num_sample, noise_seed, image_num = parse_image_info(mongo_db)
print(f"Parsed values - num_sample: {num_sample}, noise_seed: {noise_seed}, image_num: {image_num}")

# Gradients 저장 변수
gradients = {}

# 추천 위치 마스크 저장 디렉토리
output_dir = '.'

# Hook 설정 함수
def setup_hooks(generator, target_layers):
    hooks = []

    def forward_hook(module, input, output):
        module.feature_map = output

    def backward_hook(module, grad_in, grad_out):
        gradients[module.name] = grad_out[0]

    for layer_idx in target_layers:
        layer = getattr(generator.net.synthesis, f'layer{layer_idx}')
        layer.name = f'layer{layer_idx}'
        hooks.append(layer.register_forward_hook(forward_hook))
        hooks.append(layer.register_backward_hook(backward_hook))

    return hooks

# Hook 제거 함수
def remove_hooks(hooks):
    for hook in hooks:
        hook.remove()

# Grad-CAM 계산을 위한 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
generator.net.to(device)

# ΔGrad-CAM 계산을 위한 준비
latent_codes = [latent_codes1, latent_codes2]
results = []
aggregate_grad_cam = None  # 초기화
target_resolution = (256, 256)  # 원하는 Heatmap 해상도 (e.g., 최종 이미지 해상도)

sample_index = image_num  # 사용할 샘플 인덱스
step_index = 1  # 0: 조작 전, 1: 조작 후 상태

# 레이어별 비율 설정
layer_percentages = {6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0}

for layer_idx in range(6, 12):  # Layer 6~11
    grad_cams = []
    for latent_idx, latent_code in enumerate(latent_codes):
        # sample_index와 latent_code의 크기 검증
        if sample_index >= latent_code.shape[0]:
            raise IndexError(
                f"sample_index ({sample_index}) is out of bounds for latent_code with shape {latent_code.shape}"
            )

        if len(latent_code.shape) == 4:  # [N, Steps, L, D]
            if step_index >= latent_code.shape[1]:
                raise IndexError(
                    f"step_index ({step_index}) is out of bounds for latent_code with shape {latent_code.shape}"
                )
            latent_code = latent_code[sample_index, step_index, :, :]  # 샘플과 Step 선택
        elif len(latent_code.shape) == 3:  # [N, L, D]
            latent_code = latent_code[sample_index, :, :]
        else:
            raise ValueError(
                f"Unexpected latent_code shape: {latent_code.shape}. Expected 3 or 4 dimensions."
            )

        latent_code = torch.from_numpy(latent_code).unsqueeze(0).float().to(device)
        latent_code.requires_grad = True

        # Hook 설정
        hooks = setup_hooks(generator, [layer_idx])

        # Latent Code 처리
        generated_output = generator.net.synthesis(latent_code)

        # Feature Map 및 Grad-CAM 계산
        layer = getattr(generator.net.synthesis, f'layer{layer_idx}')
        feature_map = layer.feature_map
        num_channels = feature_map.shape[1]

        boundary_layer = boundary[0, :num_channels]
        boundary_broadcasted = torch.tensor(boundary_layer[:, np.newaxis, np.newaxis]).to(device)

        influence_map = torch.sum(feature_map * boundary_broadcasted, dim=[2, 3])
        top_percentage = layer_percentages.get(layer_idx, 0.1)
        num_top_channels = max(1, int(num_channels * top_percentage))
        top_channels = torch.argsort(influence_map[0], descending=True)[:num_top_channels]

        score = torch.sum(feature_map[0, top_channels])
        generator.net.zero_grad()
        score.backward(retain_graph=True)

        grad_cam = calculate_grad_cam(feature_map, gradients[layer.name])
        grad_cams.append(grad_cam)

        # Hook 제거
        remove_hooks(hooks)

    # ΔGrad-CAM 계산
    if len(grad_cams) == 2:
        grad_cam_diff = grad_cams[1] - grad_cams[0]
        grad_cam_diff = np.clip(grad_cam_diff / (grad_cam_diff.max() - grad_cam_diff.min()), 0, 1)

        # Heatmap 크기 정규화
        grad_cam_diff_resized = cv2.resize(grad_cam_diff, target_resolution)

        # ΔGrad-CAM 누적
        if aggregate_grad_cam is None:
            aggregate_grad_cam = grad_cam_diff_resized
        else:
            aggregate_grad_cam += grad_cam_diff_resized

# 최대 표시할 recommend 개수 설정
max_recommend_to_display = 3  # 최대 표시할 recommend 개수

# Aggregate ΔGrad-CAM 계산 및 DBSCAN 클러스터링
if aggregate_grad_cam is not None:
    aggregate_grad_cam_normalized = aggregate_grad_cam / aggregate_grad_cam.max()

    clusters = cluster_heatmap_with_dbscan(aggregate_grad_cam_normalized, eps=5, min_samples=40, prob_threshold=0.5)

    # 클러스터를 높은 Heat 비중으로 정렬
    cluster_scores = {
        cluster_id: np.mean(cluster_values) for cluster_id, (_, cluster_values) in clusters.items()
    }
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)

    # 최대 표시할 recommend 개수 제한
    sorted_clusters = sorted_clusters[:max_recommend_to_display]

    latent_codes1 = latent_codes1[sample_index, : , :, :]
    latent_codes2 = torch.from_numpy(latent_codes2[sample_index, step_index , :, :]).unsqueeze(0).to(device).float()  # [1, 14, 512]

    generated_image_1 = generator.easy_synthesize(latent_codes1, latent_space_type='wp')['image']
    generated_image_1 = generated_image_1[1]

    generated_image_2 = generator.net.synthesis(latent_codes2).detach().cpu().numpy()
    generated_image_2 = np.transpose(generated_image_2[0], (1, 2, 0))  # [1, 3, 256, 256] -> [256, 256, 3]
    generated_image_2 = np.clip(generated_image_2, 0, 1)

    # 최종 시각화
    result_image_2 = overlay_heatmap_on_image(generated_image_2, aggregate_grad_cam_normalized)

    # 결과 시각화: heatmap 포함 결과와 포함되지 않은 결과를 나란히 표시
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Heatmap이 포함된 결과
    mappable = axes[0].imshow(result_image_2)  # Heatmap 포함된 결과
    axes[0].set_title(f"Result with Heatmap (Top {max_recommend_to_display} Recommends)")
    plt.colorbar(mappable, ax=axes[0])  # Colorbar 추가

    scaling_factor = 3.0

    cluster_centers = []

    # 상위 recommend의 타원과 상위 포인트 표시 (Heatmap 포함된 결과)
    for i, (cluster_id, _) in enumerate(sorted_clusters):
        points, values = clusters[cluster_id]
        top_point = points[np.argmax(values)]
        y, x = top_point

       # 타원 중심과 범위 계산
        cluster_center = np.mean(points, axis=0)
        covariance_matrix = np.cov(points, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
        major_axis = scaling_factor * 2 * np.sqrt(eigenvalues[1])  # 주축
        minor_axis = scaling_factor * 2 * np.sqrt(eigenvalues[0])  # 부축

        # 타원의 각도를 항상 수직으로 설정 (90도)
        angle = 90.0
        cluster_centers.append({
        "cluster_id": cluster_id,
        "center_y": cluster_center[0],
        "center_x": cluster_center[1]
        })
        print(f"cluster_{i + 1} Center Coordinates: (y: {cluster_center[0]:.2f}, x: {cluster_center[1]:.2f})")

        # 타원 추가
        ellipse = patches.Ellipse(
            cluster_center[::-1], width=major_axis, height=minor_axis, angle=angle,
            edgecolor='red', facecolor='none', linewidth=2
        )
        axes[0].add_patch(ellipse)

        # 상위 recommend 포인트 표시
        axes[0].scatter(x, y, color='lime', edgecolors='black', linewidth=2, s=100)
        axes[0].text(x + 5, y, f"Recommend {i+1}", color='lime', fontsize=12, weight='bold')


from pymongo.errors import ConnectionFailure, PyMongoError
import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# 환경 변수 로드
try:
    load_dotenv()
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

# AWS S3 클라이언트 생성
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_s3_region
    )
except NoCredentialsError:
    print("Credentials not available for AWS S3.")
    exit(1)
except ClientError as e:
    print(f"Failed to create S3 client: {e}")
    exit(1)

# MongoDB 클라이언트 생성
try:
    client = MongoClient(mongo_uri)
    db = client["lumterior"]
    collection = db["images"]
except ConnectionFailure:
    print("Failed to connect to MongoDB.")
    exit(1)

# 최신 문서 가져오기
try:
    document = collection.find_one(sort=[('uploaded_at', -1)])
    if not document:
        print("No recent document found in MongoDB.")
        exit()
except PyMongoError as e:
    print(f"Failed to retrieve document from MongoDB: {e}")
    exit(1)

output_dir = 'masks'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

mask_images = []
for i, (cluster_id, _) in enumerate(sorted_clusters):
    try:
        points, values = clusters[cluster_id]
        top_point = points[np.argmax(values)]
        y, x = top_point

        # 타원 중심과 범위 계산
        cluster_center = np.mean(points, axis=0)
        covariance_matrix = np.cov(points, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
        major_axis = scaling_factor * 2 * np.sqrt(eigenvalues[1])  # 주축
        minor_axis = scaling_factor * 2 * np.sqrt(eigenvalues[0])  # 부축
        
        # 타원의 각도를 항상 수직으로 설정 (90도)
        angle = 90.0
        cluster_centers.append({
        "cluster_id": cluster_id,
        "center_y": cluster_center[0],
        "center_x": cluster_center[1]
        })
        print(f"cluster_{i + 1} Center Coordinates: (y: {cluster_center[0]:.2f}, x: {cluster_center[1]:.2f})")

        # 마스크 생성
        mask = np.zeros_like(aggregate_grad_cam_normalized, dtype=np.uint8)
        y, x = np.meshgrid(range(mask.shape[0]), range(mask.shape[1]), indexing='ij')
        ellipse_mask = (
            ((x - cluster_center[1]) * np.cos(np.radians(angle)) +
            (y - cluster_center[0]) * np.sin(np.radians(angle)))**2 / (major_axis / 2)**2 +
            ((x - cluster_center[1]) * np.sin(np.radians(angle)) -
            (y - cluster_center[0]) * np.cos(np.radians(angle)))**2 / (minor_axis / 2)**2
        ) <= 1  # 타원 내부인지 확인        
        
        # 타원 내부를 흰색으로 설정
        mask[ellipse_mask] = 255

        # 파일 이름 지정
        mask_filename = f"mask_cluster_{i + 1}.png"
        mask_path = os.path.join(output_dir, mask_filename)

        # 이미지 파일로 저장
        cv2.imwrite(mask_path, mask)
        
        s3_key = f'masks/{mask_filename}'
        s3.upload_file(mask_path, bucket_name, s3_key)
        mask_url = f'https://{bucket_name}.s3.{aws_s3_region}.amazonaws.com/{s3_key}'
        print(f"Uploaded {mask_filename} to {mask_url}")
        
        # round(float(cluset_center[0]),2), round(float(cluset_center[1]),2) 소수점 2자리까지 한다고하면 이걸로 교체
        mask_images.append({
            f"mask_img_{i + 1}": mask_url,
            "cluster_center": {"y": float(cluster_center[0]), "x": float(cluster_center[1])},
            "cluster_id": int(cluster_id) + 1
        })
    except cv2.error as e:
        print(f"Failed to create mask image: {e}")
    except S3UploadFailedError as e:
        print(f"Failed to upload {mask_filename} to S3: {e}")

if mask_images:
    try:
        result = collection.update_one(
            {"_id": document["_id"]},
            {"$set": {
                "mask_images": mask_images,
                "uploaded_at": datetime.now(timezone.utc)
            }}
        )
        if result.modified_count > 0:
            print(f"MongoDB updated successfully with {len(mask_images)} mask images.")
        else:
            print("MongoDB update failed. No document was modified.")
    except PyMongoError as e:
        print(f"Failed to update MongoDB: {e}")
