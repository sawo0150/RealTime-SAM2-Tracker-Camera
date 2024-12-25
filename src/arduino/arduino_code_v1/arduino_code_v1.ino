#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// PCA9685 객체 생성
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// 서보의 PWM 범위 (모터 사양에 따라 조정 필요)
#define SERVOMIN 100  // 최소 펄스 길이
#define SERVOMAX 550  // 최대 펄스 길이

void setup() {
  Serial.begin(115200);
  Serial.println("PCA9685 Serial 제어 시작");

  // PCA9685 초기화
  pwm.begin();
  pwm.setPWMFreq(50); // 서보 모터는 50Hz 주파수 사용
}

void loop() {
  // Serial 데이터가 들어왔는지 확인
    // pwm.setPWM(0, 0, 200); // 첫 번째 서보 모터 (채널 0)
    // pwm.setPWM(2, 0, 400); // 두 번째 서보 모터 (채널 2)
  if (Serial.available() > 0) {
    // 데이터 읽기 (콤마로 구분된 두 값)
    String data = Serial.readStringUntil('\n');
    int commaIndex = data.indexOf(',');

    if (commaIndex > 0) {
      // 데이터 분리
      String pwm1_str = data.substring(0, commaIndex);
      String pwm2_str = data.substring(commaIndex + 1);

      int pwm1 = pwm1_str.toInt();
      int pwm2 = pwm2_str.toInt();

      // // PWM 값 범위 제한 (SERVOMIN ~ SERVOMAX)
      // pwm1 = map(constrain(pwm1, 0, 180), 0, 180, SERVOMIN, SERVOMAX);
      // pwm2 = map(constrain(pwm2, 0, 180), 0, 180, SERVOMIN, SERVOMAX);

      // PCA9685의 0번 채널과 2번 채널에 PWM 신호 전달
      pwm.setPWM(0, 0, pwm1); // 첫 번째 서보 모터 (채널 0)
      pwm.setPWM(2, 0, pwm2); // 두 번째 서보 모터 (채널 2)

      // 디버깅 메시지
      Serial.print("Servo1 PWM: ");
      Serial.print(pwm1);
      Serial.print(", Servo2 PWM: ");
      Serial.println(pwm2);
    }
  }
}
