/*
 * Drives a DC motor on M0: forward → brake → reverse → brake.
 */

#include "RobotShield.h"

Motor motor("M0", 4, 5);  // Motor on port M0, direction pins 4 and 5

void setup() {
    Serial.begin(115200);
    I2cBus::i2c().begin();
    motor.begin();

    Serial.println("=== MotorTest Ready ===");
}

void loop() {
    Serial.println("M0: Forward 50%");
    motor.setPower(50);      // Forward at 50% power
    delay(3000);

    Serial.println("M0: Brake");
    motor.setPower(0);       // Stop (brake)
    delay(1000);

    Serial.println("M0: Reverse 50%");
    motor.setPower(-50);     // Reverse at 50% power
    delay(3000);

    Serial.println("M0: Brake");
    motor.setPower(0);       // Stop (brake)
    delay(3000);
}
