/*
 * Drives a DC motor on the Robot Shield's M0 terminal:
 * forward → stop → reverse → stop.
 *
 * M0 IN1 -> D2 (PWM)
 * M0 IN2 -> D3 (PWM)
 */

const int MOTOR_IN1_PIN = 2;  // Motor input 1 (PWM)
const int MOTOR_IN2_PIN = 3;  // Motor input 2 (PWM)

void setup() {
    Serial.begin(115200);

    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    analogWrite(MOTOR_IN1_PIN, 0);  // Motor starts stopped
    analogWrite(MOTOR_IN2_PIN, 0);

    Serial.println("=== MotorTest Ready ===");
}

void loop() {
    Serial.println("M0: Forward 50%");
    analogWrite(MOTOR_IN1_PIN, 128);   // IN1 driven, IN2 low → forward
    analogWrite(MOTOR_IN2_PIN, 0);
    delay(3000);

    Serial.println("M0: Stop");
    analogWrite(MOTOR_IN1_PIN, 0);     // Both inputs 0 → motor stops
    analogWrite(MOTOR_IN2_PIN, 0);
    delay(1000);

    Serial.println("M0: Reverse 50%");
    analogWrite(MOTOR_IN1_PIN, 0);     // Swapped: IN2 driven, IN1 low
    analogWrite(MOTOR_IN2_PIN, 128);
    delay(3000);

    Serial.println("M0: Stop");
    analogWrite(MOTOR_IN1_PIN, 0);
    analogWrite(MOTOR_IN2_PIN, 0);
    delay(3000);
}
