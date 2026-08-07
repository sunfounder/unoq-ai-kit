/*
 * Sweeps a servo on channel 0 between -45° and +45°.
 */

#include "RobotShield.h"

Servo servo(0);  // Servo on channel 0

void setup() {
    Serial.begin(115200);
    I2cBus::i2c().begin();
    servo.begin();

    Serial.println("=== ServoSweep Ready ===");
}

void loop() {
    // Sweep from -45° to +45°
    for (int16_t angle = -45; angle <= 45; angle += 2) {
        servo.setAngle(angle);
        Serial.print("Servo 0 angle: ");
        Serial.println(angle);
        delay(30);
    }

    // Sweep back from +45° to -45°
    for (int16_t angle = 45; angle >= -45; angle -= 2) {
        servo.setAngle(angle);
        Serial.print("Servo 0 angle: ");
        Serial.println(angle);
        delay(30);
    }
}
