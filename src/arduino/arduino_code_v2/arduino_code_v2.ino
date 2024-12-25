#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// PCA9685 객체 생성
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// 서보의 PWM 범위 (모터 사양에 따라 조정 필요)
#define SERVOMIN 100  // 최소 펄스 길이
#define SERVOMAX 550  // 최대 펄스 길이
#define UPDATE_INTERVAL 100 // 10Hz 주기로 업데이트 (ms 단위)

// 전역 변수 선언
int pwm1_mode = 1; // 0: 감소, 1: 정지, 2: 증가
int pwm2_mode = 1;
float speed = 2.0; // PWM 변화 속도 (float형)

// 서보 초기값 (SERVOMIN과 SERVOMAX의 평균값)
int servo1_pwm = (SERVOMIN + SERVOMAX) / 2;
int servo2_pwm = (SERVOMIN + SERVOMAX) / 2;

// 이전 업데이트 시간
unsigned long lastUpdateTime = 0;

// 시리얼 입력 버퍼
#define BUFFER_SIZE 64
char inputBuffer[BUFFER_SIZE];
unsigned int bufferIndex = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("PCA9685 Serial 제어 시작");

  // PCA9685 초기화
  pwm.begin();
  pwm.setPWMFreq(50); // 서보 모터는 50Hz 주파수 사용

  // 초기 서보 위치 설정
  pwm.setPWM(0, 0, servo1_pwm);
  pwm.setPWM(2, 0, servo2_pwm);
}

void loop() {
  // 시리얼 데이터 읽기
  while (Serial.available() > 0) {
    char inChar = Serial.read();
    // 개행 문자까지 읽음
    if (inChar == '\n') {
      inputBuffer[bufferIndex] = '\0'; // 문자열 종료
      bufferIndex = 0; // 버퍼 인덱스 초기화

      // 데이터 파싱
      int commaIndex = -1;
      for (int i = 0; i < BUFFER_SIZE; i++) {
        if (inputBuffer[i] == ',') {
          commaIndex = i;
          break;
        }
        if (inputBuffer[i] == '\0') break;
      }

      if (commaIndex > 0) {
        inputBuffer[commaIndex] = '\0'; // 콤마를 문자열 종료 문자로 변경
        String pwm1_str = String(inputBuffer);
        String pwm2_str = String(&inputBuffer[commaIndex + 1]);

        pwm1_mode = pwm1_str.toInt();
        pwm2_mode = pwm2_str.toInt();

        // 디버깅 메시지
        // Serial.print("PWM1 Mode: ");
        // Serial.print(pwm1_mode);
        // Serial.print(", PWM2 Mode: ");
        // Serial.println(pwm2_mode);
      }
    } else {
      // 버퍼 오버플로우 방지
      if (bufferIndex < BUFFER_SIZE - 1) {
        inputBuffer[bufferIndex++] = inChar;
      }
    }
  }

  // 현재 시간 확인
  unsigned long currentTime = millis();

  // 10Hz 주기로 업데이트
  if (currentTime - lastUpdateTime >= UPDATE_INTERVAL) {
    lastUpdateTime = currentTime;

    // 서보1 PWM 업데이트
    if (pwm1_mode == 2) { // 증가
      servo1_pwm += speed;
      if (servo1_pwm > SERVOMAX) servo1_pwm = SERVOMAX;
    } else if (pwm1_mode == 0) { // 감소
      servo1_pwm -= speed;
      if (servo1_pwm < SERVOMIN) servo1_pwm = SERVOMIN;
    }
    // 서보2 PWM 업데이트
    if (pwm2_mode == 2) { // 증가
      servo2_pwm += speed;
      if (servo2_pwm > SERVOMAX) servo2_pwm = SERVOMAX;
    } else if (pwm2_mode == 0) { // 감소
      servo2_pwm -= speed;
      if (servo2_pwm < SERVOMIN) servo2_pwm = SERVOMIN;
    }

    // PCA9685에 PWM 값 전달
    pwm.setPWM(0, 0, servo1_pwm);
    pwm.setPWM(2, 0, servo2_pwm);

    // 디버깅 메시지
    // Serial.print("Servo1 PWM: ");
    // Serial.print(servo1_pwm);
    // Serial.print(", Servo2 PWM: ");
    // Serial.println(servo2_pwm);
  }
}
