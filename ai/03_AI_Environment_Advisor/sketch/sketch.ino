/*
 * AI Environment Advisor
 *
 * DHT11 data  -> D4
 * Photoresistor signal -> A0
 *
 * The sketch reads the sensors every two seconds and notifies Python.
 */

#include <Arduino_RouterBridge.h>
#include "DHT.h"

const int DHT_PIN = 4;
const int LIGHT_SENSOR_PIN = A0;
const unsigned long SENSOR_INTERVAL = 2000;

#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);
unsigned long lastSensorUpdate = 0;


void sendEnvironmentData()
{
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature))
    {
        Bridge.notify("sensor_error", "Unable to read the DHT11 sensor.");
        return;
    }

    int lightRaw = analogRead(LIGHT_SENSOR_PIN);
    Bridge.notify("environment_update", temperature, humidity, lightRaw);
}


void setup()
{
    pinMode(LIGHT_SENSOR_PIN, INPUT);
    dht.begin();

    Bridge.begin();

    // Allow the DHT11 to stabilize before its first reading.
    delay(2000);
    sendEnvironmentData();
}


void loop()
{
    unsigned long now = millis();

    if (now - lastSensorUpdate >= SENSOR_INTERVAL)
    {
        lastSensorUpdate = now;
        sendEnvironmentData();
    }

    delay(10);
}
