#include <Arduino_RouterBridge.h>

const int RED_PIN = 8;
const int GREEN_PIN = 7;
const int BLUE_PIN = 6;

void setRgb(int red, int green, int blue)
{
    analogWrite(RED_PIN, constrain(red, 0, 255));
    analogWrite(GREEN_PIN, constrain(green, 0, 255));
    analogWrite(BLUE_PIN, constrain(blue, 0, 255));
}

void setup()
{
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);
    setRgb(0, 0, 0);

    Bridge.begin();
    Bridge.provide("set_rgb", setRgb);
}

void loop()
{
    delay(10);
}
