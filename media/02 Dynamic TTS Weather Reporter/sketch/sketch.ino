/*
 * Dynamic TTS Weather Reporter
 *
 * Wiring:
 *   DHT11 VCC  -> 3.3V
 *   DHT11 DATA -> D4
 *   DHT11 GND  -> GND
 *
 * Python requests the current sensor values through Bridge.
 */

    #include "DHT.h"
    #include <Arduino_RouterBridge.h>

    #define DHTPIN 4
    #define DHTTYPE DHT11

    DHT dht(DHTPIN, DHTTYPE);

    String readWeather(String message)
    {
        (void)message;

        float humidity = dht.readHumidity();
        float temperature = dht.readTemperature();

        if (isnan(humidity) || isnan(temperature)) {
            return "error";
        }

        // Return both values in one simple string:
        // temperature,humidity
        return String(temperature, 1) + "," + String(humidity, 1);
    }

    void setup()
    {
        Serial.begin(115200);
        dht.begin();

        // Give the DHT11 time to stabilize after power-on.
        delay(1000);

        Bridge.begin();
        Bridge.provide("read_weather", readWeather);

        Serial.println("Dynamic TTS Weather Reporter is ready.");
    }

    void loop()
    {
        delay(10);
    }
