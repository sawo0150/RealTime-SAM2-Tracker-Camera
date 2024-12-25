import serial
import time


# sudo chmod 666 /dev/ttyACM0
#  --> 권환 부여 해야함
# Arduino가 연결된 포트 지정 (예: COM3 또는 /dev/ttyUSB0)
arduino_port = '/dev/ttyACM0'  # 적절히 변경
baud_rate = 9600       # Arduino와 일치하도록 설정
ser = serial.Serial(arduino_port, baud_rate)

# 데이터를 보낼 함수
def send_pwm(pwm1, pwm2):
    # PWM 값을 콤마로 구분하여 문자열로 전송
    data = f"{pwm1},{pwm2}\n"
    ser.write(data.encode())  # 데이터를 바이트로 변환 후 전송
    print(f"Sent: {data.strip()}")

# 예제 실행
try:
    while True:
        # PWM 값을 동적으로 변경 (테스트용)
        pwm1 = int(input("Enter PWM for Servo1 : "))
        pwm2 = int(input("Enter PWM for Servo2 : "))
        send_pwm(pwm1, pwm2)

        time.sleep(1)  # 간격
except KeyboardInterrupt:
    print("Program stopped.")
    ser.close()
