/*
 * Cycles through 8 colors using an RGB LED and 3-channel PWM.
 */

#include "RobotShield.h"

Pwm red(6);    // Red channel on P6
Pwm green(5);  // Green channel on P5
Pwm blue(4);   // Blue channel on P4

void setup() {
    I2cBus::i2c().begin();

    red.begin();
    green.begin();
    blue.begin();

    red.setFreq(1000);
    green.setFreq(1000);
    blue.setFreq(1000);

    red.setEnable(true);
    green.setEnable(true);
    blue.setEnable(true);
}

// Set all three color channels at once
// r, g, b: pulse width from 0 (off) to 1000 (full brightness)
void setColor(uint16_t r, uint16_t g, uint16_t b) {
    red.setPulse(r);
    green.setPulse(g);
    blue.setPulse(b);
}

void loop() {
    setColor(1000, 0, 0);      // Red
    delay(1000);

    setColor(0, 1000, 0);      // Green
    delay(1000);

    setColor(0, 0, 1000);      // Blue
    delay(1000);

    setColor(1000, 1000, 0);   // Yellow   (red + green)
    delay(1000);

    setColor(0, 1000, 1000);   // Cyan     (green + blue)
    delay(1000);

    setColor(1000, 0, 1000);   // Magenta  (red + blue)
    delay(1000);

    setColor(1000, 1000, 1000);// White    (all three)
    delay(1000);

    setColor(0, 0, 0);         // Off      (none)
    delay(1000);
}
