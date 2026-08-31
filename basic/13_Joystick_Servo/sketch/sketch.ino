/*
 * Joystick Servo Control
 *
 * Joystick X (A3) -> pan servo (pin 9)
 * Joystick Y (A2) -> tilt servo (pin 10)
 * Joystick SW (D2) -> press to reset both servos to center
 */

#include <Arduino_HardwareServo.h>

const int swPin = 2, xPin = A3, yPin = A2;

HardwareServo panServo;   // Pan servo on pin 9
HardwareServo tiltServo;  // Tilt servo on pin 10

int panAngle = 90, tiltAngle = 90;  // Servo angles, 45°..135°
int xCenter = 512, yCenter = 512;
const int minAngle = 45, maxAngle = 135;
const int deadZone = 100, stepSize = 1;

void setup() {
    Serial.begin(115200);

    pinMode(swPin, INPUT_PULLUP);

    panServo.attach(9);
    tiltServo.attach(10);
    panServo.write(90);   // Center both servos
    tiltServo.write(90);

    delay(500);

    // Auto-calibrate center position
    long xTotal = 0, yTotal = 0;
    for (int i = 0; i < 20; i++) {
        xTotal += analogRead(xPin);
        yTotal += analogRead(yPin);
        delay(10);
    }
    xCenter = xTotal / 20;
    yCenter = yTotal / 20;

    Serial.println("=== Joystick Servo Control Ready ===");
}

void loop() {
    // Button press → reset to center
    if (digitalRead(swPin) == LOW) {
        panAngle = 90; tiltAngle = 90;
        panServo.write(90); tiltServo.write(90);
        delay(300); return;
    }

    int xValue = analogRead(xPin);
    int yValue = analogRead(yPin);

    // Incremental control with dead zone
    // X controls pan; Y controls tilt.
    // Pan direction is reversed so joystick left moves the platform left.
    if (xValue > xCenter + deadZone)       panAngle -= stepSize;
    else if (xValue < xCenter - deadZone)  panAngle += stepSize;
    if (yValue > yCenter + deadZone)       tiltAngle += stepSize;
    else if (yValue < yCenter - deadZone)  tiltAngle -= stepSize;

    panAngle  = constrain(panAngle, minAngle, maxAngle);
    tiltAngle = constrain(tiltAngle, minAngle, maxAngle);

    panServo.write(panAngle);
    tiltServo.write(tiltAngle);

    Serial.print("X: "); Serial.print(xValue);
    Serial.print("  Y: "); Serial.print(yValue);
    Serial.print("  Pan: "); Serial.print(panAngle);
    Serial.print("  Tilt: "); Serial.println(tiltAngle);

    delay(30);
}
