/*
 * 09 Telegram IoT Bot
 *
 * DHT11 data pin -> D2
 * External LED   -> D5
 *
 * Python uses Bridge.call() when Telegram commands arrive.
 */

#include <Arduino_RouterBridge.h>
#include <DHT.h>

const int DHT_PIN = 2;
const int LED_PIN = 5;

#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

bool ledState = false;


float getTemperature()
{
    float temperature = dht.readTemperature();

    if (isnan(temperature))
    {
        Serial.println("Failed to read temperature.");
        return 0.0;
    }

    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");

    return temperature;
}


float getHumidity()
{
    float humidity = dht.readHumidity();

    if (isnan(humidity))
    {
        Serial.println("Failed to read humidity.");
        return 0.0;
    }

    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

    return humidity;
}


void setLed(bool state)
{
    ledState = state;

    digitalWrite(
        LED_PIN,
        ledState ? HIGH : LOW
    );

    Serial.print("LED: ");
    Serial.println(ledState ? "ON" : "OFF");
}


bool getLedState()
{
    return ledState;
}


void setup()
{
    Serial.begin(115200);

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    dht.begin();

    Bridge.begin();

    Bridge.provide(
        "get_temperature",
        getTemperature
    );

    Bridge.provide(
        "get_humidity",
        getHumidity
    );

    Bridge.provide(
        "set_led",
        setLed
    );

    Bridge.provide(
        "get_led_state",
        getLedState
    );

    Serial.println("=== Telegram IoT Bot ===");
    Serial.println("DHT11: D2");
    Serial.println("External LED: D5");
    Serial.println("Ready.");
}


void loop()
{
    delay(100);
}
