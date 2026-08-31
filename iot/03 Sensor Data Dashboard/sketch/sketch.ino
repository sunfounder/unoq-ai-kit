/*
 * 03 Sensor Data Dashboard
 * Photoresistor analog output -> A0
 */

#include <Arduino_RouterBridge.h>

const int LIGHT_SENSOR_PIN = A0;
const unsigned long SAMPLE_INTERVAL = 200;

unsigned long previousSampleTime = 0;

void setup() {
    Serial.begin(115200);
    Bridge.begin();

    Serial.println("=== Sensor Data Dashboard ===");
    Serial.println("Reading light level from A0...");
}

void loop() {
    unsigned long now = millis();

    if (now - previousSampleTime < SAMPLE_INTERVAL) {
        delay(5);
        return;
    }

    previousSampleTime = now;

    int rawValue = analogRead(LIGHT_SENSOR_PIN);
    int lightLevel = map(rawValue, 0, 1023, 0, 100);
    lightLevel = constrain(lightLevel, 0, 100);

    Serial.print("Raw: ");
    Serial.print(rawValue);
    Serial.print("    Light level: ");
    Serial.print(lightLevel);
    Serial.println("%");

    Bridge.notify("update_light_level", lightLevel);
}
