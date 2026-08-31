/*
 * Reads temperature and humidity from DHT11 every 2 seconds.
 */

#include "DHT.h"

#define DHTPIN 2        // DHT11 data pin connected to pin 2
#define DHTTYPE DHT11   // DHT11 sensor type

DHT dht(DHTPIN, DHTTYPE);

unsigned long lastReadTime = 0;
const unsigned long interval = 2000;  // Read every 2 seconds

void setup() {
    Serial.begin(115200);  // Start Serial Monitor at 115200 baud
    dht.begin();            // Initialize DHT11 sensor

    Serial.println("=== DHT11 Temperature & Humidity ===");
}

void loop() {
    unsigned long currentMillis = millis();

    // Check if it's time for a new reading (non-blocking)
    if (currentMillis - lastReadTime >= interval) {
        lastReadTime = currentMillis;

        float humidity = dht.readHumidity();
        float temperature = dht.readTemperature();  // Celsius

        // Check if readings are valid
        if (isnan(humidity) || isnan(temperature)) {
            Serial.println("Failed to read from DHT11!");
            return;
        }

        Serial.print("Temperature: ");
        Serial.print(temperature);
        Serial.print(" *C   ");

        Serial.print("Humidity: ");
        Serial.print(humidity);
        Serial.println(" %");
    }
}
