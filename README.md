# subot
이제는 정말 강의를 듣고싶기 때문에 구글 삼성 페이스북이 해주기 전에 먼저 시작하는 프로젝트 입니다.     

다른 회사가 먼저 만들어낸다고 하더라도 그게 제가 원하는 중-한 실시간 번역일지는 잘 모르겠고, 원하는 모델을 입맛에 맞게 적용할 수 있다면 이 프로젝트의 의미는 충분합니다.  

이 프로젝트의 목적은 아래와 같습니다.
* OCR 로 영상에 있는 자막 실시간 인식 후 번역
* STT 로 자막이 없는 강의에 자막을 달아주는 기능 (중요)

#### OCR
![image](https://github.com/user-attachments/assets/8f0279bf-6ceb-480e-81ae-247d81c1a9c9)

제가 원하는건 중-한 번역이기 때문에 중국어의 인식률이 높은 OCR이 필요했고 baidu의 `paddleocr`을 사용하기로 결정했습니다. (이런걸 만들어주다니 압도적 감사)

#### 번역기
일단 meta의 `nllb-200-distilled-600M` 을 사용했습니다. IT 업계의 언어를 번역해버리는 상황을 피해야 되기 때문에 임시로 사용하는 모델입니다. 

<br>

# 사용법
#### 환경 세팅
개발자의 환경 세팅이기 때문에 본인에 맞는 환경을 설치하면 좋습니다. 
1. 지원하는 cuda 버전 확인
    ```bash
    nvcc -V       # cuda 설치 확인
    nvidia-smi    # 지원되는 cuda 버전 확인
    ```

2. cuda 설치   
    https://developer.nvidia.com/cuda-downloads

3. pytorch gpu 버전 명령어 확인 및 설치 
    ```bash
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    ```

4. python 3.12.7 설치

5. pip 나머지 패키지 설치
    ```bash
    git clone <this project>
    pip install -r requirements.txt
    ```

#### 실행
```bash
python ./subot.py
```
실행을 해보면 보이는 OCR Scanner 버튼으로 번역할 자막이 있는 범위를 지정하고, Translator 기능을 이용해 인식한 자막을 번역하는 것이 전부이다. 
![bandicam2024-11-1002-13-40-268-ezgif com-animated-gif-maker](https://github.com/user-attachments/assets/c3c06dd4-7038-45d6-9de0-b6dfe02a0c16)


