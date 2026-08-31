/*
 * 07 Smart Doorbell
 *
 * Push button    -> D2
 * Passive buzzer -> D5
 */

#include <Arduino_RouterBridge.h>

const int BUTTON_PIN = 2;
const int BUZZER_PIN = 5;

bool lastButtonState = HIGH;

void playDoorbellChime()
{
    // Ding
    tone(BUZZER_PIN, 1047);
    delay(300);
    noTone(BUZZER_PIN);

    delay(150);

    // Dong
    tone(BUZZER_PIN, 784);
    delay(500);
    noTone(BUZZER_PIN);

    delay(200);
}


void setup()
{
    Serial.begin(115200);

    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(BUZZER_PIN, OUTPUT);

    noTone(BUZZER_PIN);

    Bridge.begin();

    Serial.println("=== Smart Doorbell ===");
    Serial.println("Button: D2");
    Serial.println("Passive buzzer: D5");
    Serial.println("Waiting for visitors...");
}

void loop()
{
    bool buttonState = digitalRead(BUTTON_PIN);

    if (lastButtonState == HIGH &&
        buttonState == LOW)
    {
        Serial.println("Doorbell pressed");

        playDoorbellChime();
        Bridge.notify("doorbell_pressed");

        delay(80);
    }

    lastButtonState = buttonState;
    delay(10);
}
