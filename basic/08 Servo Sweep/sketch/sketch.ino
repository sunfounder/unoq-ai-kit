/*
 * Sweeps a servo between 45° and 135° (centered on 90°).
 *
 * Pan servo -> pin 9
 */

#include <Arduino_HardwareServo.h>

HardwareServo myservo;  // Pan servo on D9

void setup() {
    Serial.begin(115200);
    myservo.attach(9);

    Serial.println("=== ServoSweep Ready ===");
}

void loop() {
    // Sweep from 45° to 135° (=-45° to +45° around the 90° center)
    for (int angle = 45; angle <= 135; angle += 2) {
        myservo.write(angle);
        Serial.print("Servo angle: ");
        Serial.println(angle);
        delay(30);
    }

    // Sweep back from 135° to 45°
    for (int angle = 135; angle >= 45; angle -= 2) {
        myservo.write(angle);
        Serial.print("Servo angle: ");
        Serial.println(angle);
        delay(30);
    }
}
