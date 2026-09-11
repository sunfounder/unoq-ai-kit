/*
 * Reads an NTC thermistor and adjusts motor speed based on temperature.
 *
 * Thermistor: A1
 * Motor on the Robot Shield's M0 terminal:
 *   IN1 -> D2 (PWM)
 *   IN2 -> D3 (PWM)
 */

#include <math.h>

const int tempPin = A1;                  // Thermistor on analog pin A1
const int MOTOR_IN1_PIN = 2;             // Motor input 1 (PWM)
const int MOTOR_IN2_PIN = 3;             // Motor input 2 (PWM)

// NTC thermistor parameters (Beta model)
const float beta = 3950.0;              // Beta coefficient for this thermistor
const float seriesResistor = 10000.0;   // 10k ohm fixed resistor
const float nominalResistance = 10000.0; // Thermistor resistance at 25°C
const float nominalTemp = 25.0 + 273.15; // 25°C in Kelvin

void setup() {
    Serial.begin(115200);

    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    analogWrite(MOTOR_IN1_PIN, 0);       // Motor starts OFF
    analogWrite(MOTOR_IN2_PIN, 0);       // IN2 stays low → fan blows forward

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
        power = map((int)tempC, 25, 50, 20, 100);  // Smooth range
    }

    // Convert 0-100% to the 0-255 PWM range (IN2 stays 0 → forward)
    analogWrite(MOTOR_IN1_PIN, map(power, 0, 100, 0, 255));
    analogWrite(MOTOR_IN2_PIN, 0);

    Serial.print("Temperature: ");
    Serial.print(tempC, 1);              // Print with 1 decimal place
    Serial.print(" *C    Motor Power: ");
    Serial.print(power);
    Serial.println("%");

    delay(500);
}
