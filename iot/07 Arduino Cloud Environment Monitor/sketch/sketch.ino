/*
 * Arduino Cloud Environment Monitor
 *
 * Reads temperature and humidity from a DHT11 sensor and sends the
 * measurements to Python through Bridge. The Python App uploads them
 * to Arduino Cloud.
 *
 * The Arduino Cloud switch controls an external LED connected to D5.
 *
 * DHT11 DATA -> D4
 * External LED -> D5
 */

#include <Arduino_RouterBridge.h>
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

const int LED_PIN = 5;

// Read the DHT11 every 5 seconds.
const unsigned long SENSOR_INTERVAL = 5000;
unsigned long previousSensorMillis = 0;

void setLedState(bool state)
{
    digitalWrite(LED_PIN, state ? HIGH : LOW);

    Serial.print("LED: ");
    Serial.println(state ? "ON" : "OFF");
}

void setup()
{
    Serial.begin(115200);

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    dht.begin();

    Bridge.begin();
    Bridge.provide("set_led_state", setLedState);

    Serial.println("=== Arduino Cloud Environment Monitor ===");
    Serial.println("Waiting for DHT11 readings...");
}

void loop()
{
    unsigned long currentMillis = millis();

    // Non-blocking delay: skip until the next 5-second reading.
    if (currentMillis - previousSensorMillis < SENSOR_INTERVAL)
    {
        return;
    }

    previousSensorMillis = currentMillis;

    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature))
    {
        Serial.println("Failed to read from DHT11.");
        return;
    }

    Serial.print("Temperature: ");
    Serial.print(temperature, 1);
    Serial.print(" °C    Humidity: ");
    Serial.print(humidity, 1);
    Serial.println(" %");

    // Send the new readings to Python, which uploads them to Arduino Cloud.
    Bridge.notify(
        "update_environment_cloud",
        temperature,
        humidity
    );
}
