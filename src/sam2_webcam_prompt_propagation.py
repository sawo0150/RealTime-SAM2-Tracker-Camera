import cv2
import numpy as np
import torch
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from scipy.ndimage import morphology

# SAM2 모델 초기화
checkpoint = "./checkpoints/sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sam2_model = build_sam2(model_cfg, checkpoint, device=device)
predictor = SAM2ImagePredictor(sam2_model)

# 웹캠 설정
cap = cv2.VideoCapture(0)

# 상태 변수
click_points = []
click_labels = []
prev_mask = None  # 이전 마스크 저장
prompt_points = []  # 다음 프레임을 위한 prompt 점

# 마우스 클릭 이벤트 함수
def on_mouse_click(event, x, y, flags, param):
    global click_points, click_labels, prev_mask, prompt_points
    if event == cv2.EVENT_LBUTTONDOWN:
        # 왼쪽 클릭: 클릭한 위치를 포인트로 저장하고 라벨(1)로 표시
        click_points = [[x, y]]
        click_labels = [1]
        prev_mask = None  # 새로운 객체 선택 시 이전 마스크 초기화
        prompt_points = []  # 새로운 객체 선택 시 prompt 초기화

# 창에 마우스 이벤트 추가
cv2.namedWindow("SAM2 Webcam")
cv2.setMouseCallback("SAM2 Webcam", on_mouse_click)

# 투명한 마스크를 이미지 위에 겹쳐 표시하는 함수
def apply_transparent_mask(frame, mask, color=(0, 255, 0), alpha=0.5):
    overlay = frame.copy()
    for i in range(3):
        overlay[:, :, i] = np.where(mask == 1, frame[:, :, i] * (1 - alpha) + color[i] * alpha, frame[:, :, i])
    return overlay

# 내부 마스크 생성 및 prompt 점 추출
def create_internal_mask_and_prompts(mask, n_points=5):
    # 마스크 내부를 강조하기 위해 morphology 연산 적용
    eroded_mask = morphology.binary_erosion(mask, structure=np.ones((50, 50))).astype(np.uint8)

    # 내부 마스크에서 점 추출
    internal_indices = np.argwhere(eroded_mask > 0)
    if len(internal_indices) == 0:
        return None, []
    selected_indices = internal_indices[np.linspace(0, len(internal_indices) - 1, n_points, dtype=int)]
    prompt_points = [[int(x), int(y)] for y, x in selected_indices]  # (y, x)를 (x, y)로 변환
    return eroded_mask, prompt_points

with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=torch.cuda.is_available()):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 이미지 초기화 및 객체 추적
        predictor.set_image(frame)

        if prev_mask is not None and prompt_points:
            # 이전 프레임의 prompt 점을 사용하여 마스크 생성
            input_points = np.array(prompt_points)
            input_labels = np.ones(len(prompt_points), dtype=np.int32)
            masks, scores, _ = predictor.predict(
                point_coords=input_points,
                point_labels=input_labels,
                multimask_output=False
            )
            prev_mask = masks[0]  # numpy 형식으로 저장

            # 마스크 내부에서 prompt 점 갱신
            prev_mask_internal, prompt_points = create_internal_mask_and_prompts(prev_mask)
        elif click_points:
            # 클릭된 좌표를 사용하여 새로운 마스크 생성
            input_points = np.array(click_points)
            input_labels = np.array(click_labels)
            masks, scores, _ = predictor.predict(
                point_coords=input_points,
                point_labels=input_labels,
                multimask_output=False
            )
            prev_mask = masks[0]  # numpy 형식으로 저장

            # 마스크 내부에서 prompt 점 추출
            prev_mask_internal, prompt_points = create_internal_mask_and_prompts(prev_mask)

        # 마스크를 화면에 표시
        if prev_mask is not None:
            frame = apply_transparent_mask(frame, prev_mask, color=(0, 255, 0), alpha=0.5)

        # 클릭된 위치 및 prompt 점을 표시
        if click_points:
            for point in click_points:
                cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)
        if prompt_points:
            for point in prompt_points:
                cv2.circle(frame, (point[0], point[1]), 3, (255, 0, 0), -1)

        # 화면에 이미지 출력
        cv2.imshow("SAM2 Webcam", frame)

        # 키보드 입력 처리
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break  # 'q'를 누르면 종료
        elif key & 0xFF == ord('x'):
            # 'x'를 누르면 상태 초기화
            click_points.clear()
            click_labels.clear()
            prev_mask = None
            prompt_points = []

cap.release()
cv2.destroyAllWindows()
