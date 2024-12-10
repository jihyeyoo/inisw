# 고려대학교 지능정보 SW 아카데미 5기 2조
![header](https://capsule-render.vercel.app/api?type=waving&color=black&height=300&section=header&text=LumTerior&fontSize=90&fontColor=ECD77F&animation=fadeIn&fontAlignY=38&desc=조명이%20바뀌면%20가치도%20바뀝니다.&descAlignY=55&descAlign=70)

## :busts_in_silhouette: Members

| 안지홍 | 유지혜 | 이승재 |
|---|---|---|
| __이정현__ | __하동우__ | __홍규린__ |

<br>

## :link: Resource

[Notion](https://www.notion.so/fenetre/2-94058050e52b422c88456d5acff4bea4)

<br>

## :computer: Tech Stacks

<div > 
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
  <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white"> 
  <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black">
  <img src="https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white"> 
	<br>
  <img src="https://img.shields.io/badge/mongoDB-47A248?style=for-the-badge&logo=MongoDB&logoColor=white">
  <img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
	
</div>

<br>

## :round_pushpin: **Introduction**



조명은 실내 공간의 분위기를 결정짓는 핵심 요소입니다. 하지만 대부분의 사용자들은 공간 구조나 사용 목적에 맞는 최적의 조명 배치와 효과를 결정하는 데 어려움을 겪습니다. 현재까지의 솔루션은 정적인 가이드나 전문가 의존 방식에 치우쳐 있어, 비용과 시간적 부담이 큽니다.

본 프로젝트는 **생성형 모델(GAN)**, **Grad-CAM**, **Diffusion Model** 기술을 결합하여 기존과는 다른 방식으로 조명 배치와 효과를 추천하는 새로운 접근법을 제안합니다.

- **배치 추천**: 공간 내에서 조명을 배치할 최적의 위치를 학습하고 추천합니다.
- **조명 효과 적용**: 추천된 위치에 조명 효과(밝기, 색온도, 확산 등)를 사실적으로 적용합니다.

이 시스템은 사용자 입력을 최소화하면서도, 최적화된 배치와 효과 적용 결과를 제공합니다. 이는 사용자의 의사결정을 단순화하고, 결과를 사전에 검토할 수 있는 기회를 제공합니다.
<br/>
<br/>
## :key: **Key Features**



### **1. 배치 추천**

- 업로드한 공간 이미지를 분석하여 조명을 배치할 최적의 위치를 제안합니다.
- 공간 구조, 크기, 사용 목적에 기반한 맞춤형 추천 결과를 제공합니다.
- 학습된 데이터 기반으로 다양한 배치 후보를 제공합니다.

### **2. 조명 효과 적용**

- 추천된 위치에 조명 효과(밝기, 색온도, 확산 등)를 시뮬레이션하여 적용합니다.
- **Diffusion Model**을 활용해 실제와 유사한 조명 이미지를 생성합니다.
- 선택한 배치와 조명 효과를 적용한 결과를 비교하여 최적의 선택을 돕습니다.

<br/>
<br/>

## **Colab QuickStart**

[[예시데이터 생성](https://colab.research.google.com/drive/1gdmoDPuyOJKogsPuvj9BmficmRiDbomB)]
[[배치 추천](https://colab.research.google.com/drive/1U4E21tIwgUvybyZYvlB4m4CnWCxLP0ex)]
[[조명 적용](https://gudong0918.tistory.com/104?category=1198432)]

<br/>
<br/>


## **Flow Chart**

### **1. 배치 추천**

![ㅇㅇㅇㅇㅇ (5)](https://github.com/user-attachments/assets/0a1625ec-5da9-4743-9389-cd1aca04c8be)

### **2. 조명 적용**

![ㅇㅇㅇㅇㅇ (6)](https://github.com/user-attachments/assets/d5ca457f-5a8b-4c25-939a-68fc06eae17f)

<br/>
<br/>

## :arrow_right_hook: **Service Flow**



1. **공간 이미지 업로드**
   - 사용자가 자신의 공간 사진을 시스템에 업로드합니다.

2. **GAN을 활용한 조명 관련 특징 추출**
   - GAN으로 학습된 패턴을 기반으로 공간 내 **조명 배치와 관련된 주요 특징**을 분석합니다.
   - 이를 통해 조명의 공간적 특징을 반영한 feature map을 생성합니다.
  
3. **Grad-CAM을 이용한 주요 영역 분석**
   - 생성된 후보 이미지에 대해 Grad-CAM을 적용해 **조명이 강조되는 주요 영역**을 시각적으로 분석합니다.
   - 사용자는 Grad-CAM의 결과를 통해 각 조명 배치의 적합성과 중요도를 확인할 수 있습니다.
  
4. **Diffusion Model을 활용한 조명 효과 적용**
   - Grad-CAM 결과를 기반으로 사용자가 원하는 배치를 선택합니다.
   - 선택된 배치에 대해 Diffusion Model을 활용하여 선택된 조명을 사실적으로 합성합니다.
   - 조명의 밝기, 색온도를 적용해 최종 이미지를 생성합니다.

5. **최종 결과 확인 및 선택**
   - 사용자에게 조명 배치와 효과가 적용된 이미지를 제공합니다.
   - 생성된 이미지 옵션을 비교하고 최적의 배치를 선택합니다.
  
<br/>
<br/>


## **Approach**



### **1. GAN (Generative Adversarial Network)**
***

### **Why Generative Models?**
- **Unanswered Spatial Problems**: 조명 배치와 같은 문제는 정답이 정해져 있지 않으며, 이를 해결하기 위해 **새로운 패턴 생성**이 필요.
- **Feature-based Decision Making**: 조명 배치의 최적화를 위해 공간적 특징과 조명의 영향을 모델링할 수 있는 도구가 필요.
- **Flexibility**: 조명 배치처럼 복잡하고 다층적인 문제를 해결하기 위해 잠재 공간(latent space)을 활용해 다차원적 솔루션을 제공.


#### **Why GAN?**

- **Feature Map Extraction**: GAN은 이미지 생성뿐 아니라, 조명 배치에 영향을 미치는 특징(feature map)과 파라미터(latent representation)를 추출하는 데 강력한 도구.
- **Pattern Recognition**: GAN으로 학습된 데이터는 공간적 배치와 조명 배치 간의 관계를 모델링할 수 있음.
- **Scalable Application**: 다양한 조명 배치 후보를 생성하는 대신, 조명 배치에 필요한 **기저 패턴**을 학습하여 더 빠르게 유효한 결과를 도출.


#### **Why StyleGAN?**

- **Fine-grained Control**: StyleGAN은 Latent Space를 조정해 세부적인 조명 배치 변화를 적용할 수 있습니다.
- **High-quality Output**: 기존 GAN 모델보다 더 자연스럽고 고해상도의 이미지를 생성 가능합니다.
- **Layer-wise Manipulation**: 특정 레이어를 선택하여 조명 배치 관련 특성을 강조하거나 수정 가능합니다.
- **커뮤니티 지원 및 검증된 성능**: StyleGAN은 다양한 연구와 커뮤니티에서 성능이 검증된 모델로, 조명 배치처럼 세부적인 조정이 필요한 작업에 적합합니다.

<br/>

### **2. CAM (Class Activation Map)**
***
#### **Why CAM?**

- CAM은 모델이 예측에 사용한 영역을 시각적으로 표현할 수 있어 배치 추천의 타당성을 설명 가능합니다.
- 조명 배치 추천에서 중요한 영역을 명확히 정의하는 데 사용됩니다.

#### **Why Grad-CAM?**

- **General Applicability**: CNN 기반 모델의 어떤 아키텍처에도 적용 가능합니다.
- **Interpretability**: Grad-CAM은 조명 배치의 주요 영향을 미치는 공간적 영역을 효과적으로 강조합니다.
- **Integration with GAN**: StyleGAN에서 생성한 이미지를 Grad-CAM으로 분석해, 조명 배치의 적합성을 평가합니다.
- **ReLU Activation**: 조명의 밝기와 같은 긍정적인 영향을 중심으로 시각화를 제공합니다.

<br/>

### **3. SVM Manipulation**
***
#### **Why SVM?**

- **Boundary Learning**: SVM은 데이터를 분류하고 조명 배치와 관련된 중요한 특징들을 구분하는 경계를 학습합니다.
- **Flexibility**: 조명 배치 문제에 대해 다차원 공간에서 효과적인 분류와 학습이 가능합니다.
- **Interpretable Model**: SVM에서 학습된 경계는 조명 배치의 결정 과정에 대해 직관적이고 해석 가능합니다.

#### **How SVM is Used?**

1. **Boundary Definition**: Latent Space에서 특정 조명 배치에 해당하는 경계를 학습합니다.
2. **Layer Manipulation**: StyleGAN의 특정 레이어를 조정하여, 조명 배치와 관련된 Latent Code를 조작합니다.

<br/>

### **4. Diffusion Model (Paint by example)**
***
#### **Why Diffusion Model?**

- 조명 효과를 포함한 정교한 합성 결과를 생성합니다.
- 사용자가 배치한 조명의 물리적 특성을 재현하여 설득력 있는 결과를 제공합니다.

<br/>
<br/>




## **Expected Outcomes**



1. **사용자 경험 개선**
   - 조명 배치와 효과 적용 과정을 자동화하여 의사결정 과정을 단순화합니다.
   - 실제 설치 전에 시뮬레이션 이미지를 제공해 사용자 만족도를 높입니다.
2. **공간 활용 최적화**
   - 데이터 기반으로 조명을 배치해 공간의 활용성을 극대화합니다.
   - 맞춤형 조명 효과로 공간의 미적 가치와 기능성을 동시에 증대합니다.
3. **비용 및 시간 절감**
   - 전문가 의존도를 낮춰 설치 비용을 절감하고, 조명 배치에 대한 실험적 접근을 최소화합니다.
  
<br/>
<br/>

## **Future Improvement**

### 1. 조명 배치 추천의 고도화
- **사용자 선호 데이터 기반 학습**  
  - 사용자의 선택 데이터를 지속적으로 학습하여, 개인화된 조명 배치 추천을 구현합니다.  
  - 조명 위치뿐만 아니라 조명 기구의 디자인, 색상 등도 고려한 다차원적인 추천으로 확장할 수 있습니다.  
- **다양한 공간 유형에 대한 적용**  
  - 거실, 침실 등 특정 공간을 넘어 실외 조명이나 상업 공간(예: 카페, 갤러리)으로 확장하여 사용 사례를 다각화할 수 있습니다.  


### 2. 기술의 다른 활용 사례
- **인테리어 최적화 시스템**  
  - 조명뿐만 아니라 가구 배치, 색상 조합 등 공간의 전체적인 구성을 추천하는 통합 솔루션으로 확장 가능합니다.  
- **조명 제조사와의 협업**  
  - 추천된 조명 배치를 기반으로 조명 기구를 직접 추천하거나, 커스터마이징된 제품을 제작할 수 있는 플랫폼으로 활용할 수 있습니다. 



### 3. 기술 성능 개선
- **추가적인 데이터셋 학습**  
  - 다양한 인테리어 플랫폼들을 통해 실내 공간 데이터셋을 추가로 학습시켜 다양한 공간 조건에서 더 정교한 배치 추천이 가능하도록 개선합니다.  
- **SVM과 Diffusion Model의 통합 최적화**  
  - SVM 기반 Boundary Manipulation의 효율성을 높이고, Diffusion Model과의 상호작용을 개선하여 더 정밀한 결과를 제공.  

