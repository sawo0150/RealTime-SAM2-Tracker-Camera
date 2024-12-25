import cv2

# 웹캠을 열기 - 기본 웹캠은 장치 번호 0으로 설정
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

while True:
    # 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽어올 수 없습니다.")
        break

    # 프레임을 화면에 표시
    cv2.imshow("Webcam Frame", frame)

    # 'q' 키를 누르면 루프 탈출
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
