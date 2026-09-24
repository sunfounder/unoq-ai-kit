/*
 * 08 AI Story Dice
 *
 * The UNO Q LED matrix displays the current story mood:
 * 0 = calm, 1 = happy, 2 = mysterious, 3 = exciting
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_LED_Matrix.h>

Arduino_LED_Matrix matrix;

const uint8_t CALM_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,7,7,7,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0
};

const uint8_t HAPPY_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,7,0,0,0,0,0,0,0,7,0,0,
  0,0,0,7,0,0,0,0,0,7,0,0,0,
  0,0,0,0,7,7,7,7,7,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0
};

const uint8_t MYSTERIOUS_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,7,7,7,0,0,0,0,
  0,0,0,0,0,0,0,0,7,0,0,0,0,
  0,0,0,0,0,0,0,7,0,0,0,0,0,
  0,0,0,0,0,0,0,7,0,0,0,0,0
};

const uint8_t EXCITING_FACE[104] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,7,7,0,0,0,7,7,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,7,7,7,0,0,0,0,0,
  0,0,0,0,7,0,0,0,7,0,0,0,0,
  0,0,0,0,0,7,7,7,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0
};

void show_story_mood(int code)
{
  switch (code) {
    case 1: matrix.draw(HAPPY_FACE);      break;
    case 2: matrix.draw(MYSTERIOUS_FACE); break;
    case 3: matrix.draw(EXCITING_FACE);   break;
    default: matrix.draw(CALM_FACE);      break;
  }
}

void setup()
{
  matrix.begin();
  matrix.setGrayscaleBits(3);
  matrix.clear();
  matrix.draw(CALM_FACE);

  Bridge.begin();
  Bridge.provide("show_story_mood", show_story_mood);
}

void loop()
{
  delay(50);
}
