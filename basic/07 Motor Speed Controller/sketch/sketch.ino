/*
 * Drives a DC motor on the Robot Shield's M0 terminal:
 * forward → stop → reverse → stop.
 *
 * M0 direction pin -> D4
 * M0 PWM pin       -> D5
 */

const int motorDirPin = 4;  // Motor direction control
const int motorPwmPin = 5;  // Motor speed control (PWM)

void setup() {
    Serial.begin(115200);

    pinMode(motorDirPin, OUTPUT);
    pinMode(motorPwmPin, OUTPUT);
    analogWrite(motorPwmPin, 0);  // Motor starts stopped

    Serial.println("=== MotorTest Ready ===");
}

void loop() {
    Serial.println("M0: Forward 50%");
    digitalWrite(motorDirPin, HIGH);   // Forward direction
    analogWrite(motorPwmPin, 128);     // ~50% speed (0-255)
    delay(3000);

    Serial.println("M0: Stop");
    analogWrite(motorPwmPin, 0);       // Stop the motor
    delay(1000);

    Serial.println("M0: Reverse 50%");
    digitalWrite(motorDirPin, LOW);    // Reverse direction
    analogWrite(motorPwmPin, 128);     // ~50% speed
    delay(3000);

    Serial.println("M0: Stop");
    analogWrite(motorPwmPin, 0);       // Stop the motor
    delay(3000);
}
