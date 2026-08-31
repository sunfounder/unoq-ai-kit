/*
 * Cycles through 8 colors using an RGB LED and analogWrite().
 *
 * Red   -> D8
 * Green -> D7
 * Blue  -> D6
 */

const int redPin = 8;
const int greenPin = 7;
const int bluePin = 6;

void setup() {
    pinMode(redPin, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(bluePin, OUTPUT);
}

// Set all three color channels at once
// r, g, b: brightness from 0 (off) to 255 (full brightness)
void setColor(int r, int g, int b) {
    analogWrite(redPin, r);
    analogWrite(greenPin, g);
    analogWrite(bluePin, b);
}

void loop() {
    setColor(255, 0, 0);      // Red
    delay(1000);

    setColor(0, 255, 0);      // Green
    delay(1000);

    setColor(0, 0, 255);      // Blue
    delay(1000);

    setColor(255, 255, 0);    // Yellow   (red + green)
    delay(1000);

    setColor(0, 255, 255);    // Cyan     (green + blue)
    delay(1000);

    setColor(255, 0, 255);    // Magenta  (red + blue)
    delay(1000);

    setColor(255, 255, 255);  // White    (all three)
    delay(1000);

    setColor(0, 0, 0);        // Off      (none)
    delay(1000);
}
