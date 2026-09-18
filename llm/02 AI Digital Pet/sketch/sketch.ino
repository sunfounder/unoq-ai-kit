/*
 * AI Digital Pet
 *
 * The Python app sends an emotion code through Bridge. The sketch displays
 * the matching face on the UNO Q 8x13 LED matrix.
 *
 * 0 = neutral, 1 = happy, 2 = sad, 3 = surprised, 4 = thinking
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_LED_Matrix.h>

Arduino_LED_Matrix matrix;

// Each frame contains 8 rows x 13 columns. Brightness values range from 0–7.
uint8_t NEUTRAL_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,7,7,7,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0
};

uint8_t HAPPY_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,7,0,0,0,0,0,0,0,7,0,0,
  0,0,0,7,0,0,0,0,0,7,0,0,0,
  0,0,0,0,7,7,7,7,7,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0
};

uint8_t SAD_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,7,7,7,7,7,0,0,0,0,
  0,0,0,7,0,0,0,0,0,7,0,0,0,
  0,0,7,0,0,0,0,0,0,0,7,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0
};

uint8_t SURPRISED_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,7,7,7,0,0,0,0,0,
  0,0,0,0,7,0,0,0,7,0,0,0,0,
  0,0,0,0,0,7,7,7,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0
};

uint8_t THINKING_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,7,7,7,0,0,0,0,
  0,0,0,0,0,0,0,0,7,0,0,0,0,
  0,0,0,0,0,0,0,7,0,0,0,0,0,
  0,0,0,0,0,0,0,7,0,0,0,0,0
};

void show_emotion(int code)
{
  switch (code) {
    case 1: matrix.draw(HAPPY_FACE);     break;
    case 2: matrix.draw(SAD_FACE);       break;
    case 3: matrix.draw(SURPRISED_FACE); break;
    case 4: matrix.draw(THINKING_FACE);  break;
    default: matrix.draw(NEUTRAL_FACE);  break;
  }
}

void setup()
{
  matrix.begin();
  matrix.setGrayscaleBits(3);
  matrix.clear();
  matrix.draw(NEUTRAL_FACE);

  Bridge.begin();
  Bridge.provide("show_emotion", show_emotion);
}

void loop()
{
  delay(50);
}
