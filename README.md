
---

## **RealTime-SAM2-Tracker-Camera**

> **SAM2 모델을 활용해 마우스 클릭(프롬프트)만으로 실시간 객체를 세그먼트·추적하고 웹캠을 자동 제어하는 프로젝트**  

<br/>

### 1. About This Project
- **프로젝트 개요**  
  - 본 프로젝트는 **2024 서울대학교 LnL의 "뇌과학으로 바라보는 인공지능" 학생자율세미나**에서 진행되었습니다.  
  - Meta의 **Segment Anything Model 2 (SAM2)** 를 적용하여 사용자가 클릭한 객체를 실시간으로 세그먼트(분할)하고, 해당 객체가 화면 중앙에 위치하도록 서보모터로 웹캠을 제어합니다.
  - Prompt(마우스 클릭)만으로 다양한 물체를 빠르게 추적할 수 있으므로, 홈캠·로봇 비전·MR 등 다양한 분야에 적용할 수 있습니다.
  - 추가 설명 : [github-blog Link](https://sawo0150.github.io/RealTime-SAM2-Tracker-Camera/)
<br/>

### 2. Team Members & Roles
- **박상원**: 코드 제작 및 모터 제어 코드 작성  
- **이승재**: SAM2 논문 조사 및 보고서 작성  
- **이윤수**: Webcam 3D 모델링  

<br/>

### 3. Features
1. **Prompt 기반 실시간 세그먼트**  
   - 마우스 클릭 또는 Box 지정 등으로 프롬프트가 주어지면, SAM2가 곧바로 객체 마스크를 예측하고 화면에 표시
2. **서보모터 자동 제어**  
   - 선택된 물체 중심과 화면 중심 위치를 비교해, MG996R 180도 서보모터(Joint1, Joint2)를 제어  
   - 좌우·상하 회전을 통해 물체가 항상 화면 중앙에 위치하도록 추적
3. **높은 확장성**  
   - SAM2 오픈소스 특성을 활용하여 추가 파인튜닝 없이도 다양한 유형의 객체 인식 가능

<br/>

### 4. Demo Videos

1. **2024 뇌과학으로 바라보는 인공지능 세미나 - 웹캠 테스트 (웹캠 동작 영상)**  
   [![Webcam Demo](https://img.youtube.com/vi/YOsFoMNbPqE/0.jpg)](https://youtu.be/YOsFoMNbPqE)  
   [https://youtu.be/YOsFoMNbPqE](https://youtu.be/YOsFoMNbPqE)

2. **2024 뇌과학으로 바라보는 인공지능 세미나 - 웹캠 테스트 (사물 추적)**  
   [![Object Tracking Demo](https://img.youtube.com/vi/RFHs3VO69co/0.jpg)](https://youtu.be/RFHs3VO69co)  
   [https://youtu.be/RFHs3VO69co](https://youtu.be/RFHs3VO69co)

3. **2024 뇌과학으로 바라보는 인공지능 세미나 - 웹캠 테스트 (사람 추적)**  
   [![Person Tracking Demo](https://img.youtube.com/vi/V4sBBPQ_77k/0.jpg)](https://youtu.be/V4sBBPQ_77k)  
   [https://youtu.be/V4sBBPQ_77k](https://youtu.be/V4sBBPQ_77k)

<br/>

### 5. Requirements
- **OS**: Ubuntu 22.04 (기타 Linux 계열 환경에서도 동작 가능)  
- **Python**: 3.8 이상  
- **하드웨어**:  
  - MG996R 180도 서보모터 (2개)  
  - PCA9685 Servo Driver
  - USB 웹캠  
- **Dependencies** (예시):
  ```bash
  pip install opencv-python==4.5.5.64
  pip install torch==2.0.1
  pip install numpy==1.23.5
  # 기타 필요 라이브러리
  ```
- **SAM2 모델**: [facebookresearch/sam2](https://github.com/facebookresearch/sam2)

<br/>

### 6. Usage

1. **프로젝트 클론**
   ```bash
   git https://github.com/sawo0150/RealTime-SAM2-Tracker-Camera.git
   cd RealTime-SAM2-Tracker-Camera
   ```

2. **SAM2 레포지토리 준비**
   - [facebookresearch/sam2](https://github.com/facebookresearch/sam2) 저장소를 로컬에 클론
   - SAM2 레포지토리 설명에 따라 설치

3. **하드웨어 연결**
   - MG996R 서보모터 2축(좌우 회전, 상하 회전)
   - Arduino - PCA9685 직접 PWM 핀 연결
   - 웹캠 USB 연결

4. **메인 스크립트 실행**
   ```bash
   python3 src/webcam_publisher.py
   ```
   Arduino : src/arduino/arduino_code_v2/arduino_code_v2.ino 실행
   
   - 실행 후 웹캠 창이 뜨면, 추적할 객체를 마우스로 클릭  
   - 선택된 객체(초록색 마스크)가 화면 중앙에 오도록 자동 추적 & 웹캠 회전

<br/>

### 7. Notes
- **실시간성**을 위해 GPU 사용(CUDA 환경) 권장
- 서보모터와 Arduino 간 통신 시 `serial` 보드레이트 설정 필수 확인
- 3D 프린팅 STL 파일 등은 `3D_models/` 폴더나 별도 링크로 공유 가능 (이런걸 만들고 싶다면 직접 하는게 나을듯...)

<br/>

### 8. References
- Kirillov, A., et al. (2023). **Segment Anything**. Meta AI Research  
- Ravi, N., et al. (2024). **SAM 2: Segment Anything in Images and Videos**. Meta AI Research  
- [facebookresearch/sam2](https://github.com/facebookresearch/sam2)

---
