/*
 * Hold both servos at 90 degrees for pan-tilt assembly.
 * Pan servo: D9
 * Tilt servo: D10
 */

#include <Arduino_HardwareServo.h>

HardwareServo panServo;
HardwareServo tiltServo;

void setup() {
    panServo.attach(9);
    tiltServo.attach(10);
}

void loop() {
    panServo.write(90);
    tiltServo.write(90);
    delay(100);
}
