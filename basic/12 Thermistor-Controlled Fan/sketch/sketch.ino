/*
 * Reads an NTC thermistor and adjusts motor speed based on temperature.
 */

#include "RobotShield.h"
#include <math.h>

const int tempPin = A0;                  // Thermistor on analog pin A0
Motor motor("M0", 4, 5);                // Motor on port M0

// NTC thermistor parameters (Beta model)
const float beta = 3950.0;              // Beta coefficient for this thermistor
const float seriesResistor = 10000.0;   // 10k ohm fixed resistor
const float nominalResistance = 10000.0; // Thermistor resistance at 25°C
const float nominalTemp = 25.0 + 273.15; // 25°C in Kelvin

void setup() {
    Serial.begin(115200);

    I2cBus::i2c().begin();
    motor.begin();
    motor.setPower(0);                   // Motor starts OFF

    Serial.println("=== Temperature Controlled Motor ===");
}

void loop() {
    int adcValue = analogRead(tempPin);  // Read thermistor voltage (0–1023)

    // Step 1: Calculate thermistor resistance
    float resistance = (1023.0 / adcValue - 1.0) * seriesResistor;

    // Step 2: Convert resistance to temperature (Beta equation)
    float tempC = 1.0 / (log(resistance / nominalResistance) / beta
                   + 1.0 / nominalTemp) - 273.15;

    // Step 3: Map temperature to motor power
    int power;
    if (tempC < 25) {
        power = 0;                       // Below 25°C: fan OFF
    } else if (tempC > 50) {
        power = 100;                     // Above 50°C: fan at MAX
    } else {
        power = map((int)tempC, 25, 50, 0, 100);  // Smooth range
    }

    motor.setPower(power);

    Serial.print("Temperature: ");
    Serial.print(tempC, 1);              // Print with 1 decimal place
    Serial.print(" *C    Motor Power: ");
    Serial.print(power);
    Serial.println("%");

    delay(500);
}
