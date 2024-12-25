import cv2
import numpy as np
import torch
import serial
import time
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

# Arduino 시리얼 설정
arduino_port = '/dev/ttyACM0'  # Arduino 포트
baud_rate = 115200  # Arduino의 Baud rate
ser = serial.Serial(arduino_port, baud_rate)

# 이전 PWM 상태 저장
previous_pwm1 = None
previous_pwm2 = None

print (ser.readline())  #==> 매우 중요!! - 안하면 오류남
# PWM 값을 전송하는 함수
def send_pwm(pwm1, pwm2):
    global previous_pwm1, previous_pwm2

    # 상태가 변경된 경우에만 전송
    if pwm1 != previous_pwm1 or pwm2 != previous_pwm2:
        data = f"{pwm1},{pwm2}\n"
        ser.write(data.encode())
        print(f"Sent: {data.strip()}")

        # 이전 상태 업데이트
        previous_pwm1 = pwm1
        previous_pwm2 = pwm2

# SAM2 모델 초기화
checkpoint = "./checkpoints/sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sam2_model = build_sam2(model_cfg, checkpoint, device=device)
predictor = SAM2ImagePredictor(sam2_model)

# 웹캠 설정
cap = cv2.VideoCapture(0)

# 클릭한 좌표와 라벨을 저장하는 리스트
click_points = []
click_labels = []

# 마우스 클릭 이벤트 함수
def on_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # 왼쪽 클릭: 클릭한 위치를 포인트로 저장하고 라벨(1)로 표시
        click_points.append([x, y])
        click_labels.append(1)

# 마스크의 중심을 계산하는 함수
def get_mask_center(mask):
    indices = np.argwhere(mask)
    if indices.size == 0:
        return None  # 마스크가 없으면 None 반환
    center = indices.mean(axis=0).astype(int)
    return center[1], center[0]  # (x, y) 형태로 반환

# 창에 마우스 이벤트 추가
cv2.namedWindow("SAM2 Webcam")
cv2.setMouseCallback("SAM2 Webcam", on_mouse_click)

# 투명한 마스크를 이미지 위에 겹쳐 표시하는 함수
def apply_transparent_mask(frame, mask, color=(0, 255, 0), alpha=0.5):
    overlay = frame.copy()
    for i in range(3):
        overlay[:, :, i] = np.where(mask == 1, frame[:, :, i] * (1 - alpha) + color[i] * alpha, frame[:, :, i])
    return overlay

# 화면 중심 좌표 계산
def get_screen_center(frame):
    height, width = frame.shape[:2]
    return width // 2, height // 2

# 서보 모터 제어
def control_servos(center, screen_center):
    screen_center_x, screen_center_y = screen_center
    center_x, center_y = center

    # PWM 값 결정
    if abs(center_x - screen_center_x) < 50:
        pwm1 = 1
    elif center_x > screen_center_x + 50:
        pwm1 = 0
    else:
        pwm1 = 2

    if abs(center_y - screen_center_y) < 50:
        pwm2 = 1
    elif center_y < screen_center_y - 50:
        pwm2 = 2
    else:
        pwm2 = 0

    # 변경된 PWM 값만 전송
    send_pwm(pwm1, pwm2)

# 메인 루프
with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 이미지 초기화 및 클릭된 좌표를 사용하여 객체 인식
        predictor.set_image(frame)
        if click_points:
            # 클릭된 좌표를 numpy 배열로 변환
            input_points = np.array(click_points)
            input_labels = np.array(click_labels)

            # SAM2를 사용하여 마스크 예측
            masks, scores, _ = predictor.predict(
                point_coords=input_points,
                point_labels=input_labels,
                multimask_output=False
            )

            # 예측된 마스크를 처리
            for i, mask in enumerate(masks):
                # 마스크의 중심 위치 계산
                mask_center = get_mask_center(mask)
                click_points[i] = mask_center
                if mask_center is not None:
                    # 화면 중심 좌표와 비교하여 서보 모터 제어
                    screen_center = get_screen_center(frame)
                    control_servos(mask_center, screen_center)

            # 클릭된 위치를 표시
            for point in input_points:
                cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)

            # 마스크를 화면에 표시
            if masks is not None:
                frame = apply_transparent_mask(frame, masks[0], color=(0, 255, 0), alpha=0.5)

        # 화면에 이미지 출력
        cv2.imshow("SAM2 Webcam", frame)

        # 키보드 입력 처리
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break  # 'q'를 누르면 종료
        elif key & 0xFF == ord('x'):
            # 'x'를 누르면 클릭 정보 초기화
            click_points.clear()
            click_labels.clear()

cap.release()
cv2.destroyAllWindows()
ser.close()
