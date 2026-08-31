/*
 * LED Matrix Patterns
 *
 * Displays five simple patterns in sequence:
 * Heart -> Star -> Smile -> Arrow -> Check
 */

#include <Arduino_LED_Matrix.h>
#include "matrix_patterns.h"

Arduino_LED_Matrix matrix;

const unsigned long DISPLAY_TIME = 1000;

void showPattern(uint8_t pattern[8][13]) {
    matrix.renderBitmap(pattern, 8, 13);
    delay(DISPLAY_TIME);
}

void setup() {
    matrix.begin();
    matrix.clear();
}

void loop() {
    showPattern(HEART);
    showPattern(STAR);
    showPattern(SMILE);
    showPattern(ARROW);
    showPattern(CHECK);
}
