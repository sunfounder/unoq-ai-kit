/*
 * A 4-level LED bar graph that responds to ambient light.
 */

const int lightPin = A0;               // Photoresistor on analog pin A0
const int ledPins[] = {2, 3, 4, 5};   // LEDs on digital pins D2–D5

void setup() {
    Serial.begin(115200);

    // Initialize all 4 LEDs at once with a for loop
    for (int i = 0; i < 4; i++) {
        pinMode(ledPins[i], OUTPUT);
        digitalWrite(ledPins[i], LOW);
    }

    Serial.println("=== Light Sensor LED Indicator ===");
}

void loop() {
    int lightValue = analogRead(lightPin);           // Read light sensor (0–1023)
    int level = map(lightValue, 0, 1023, 1, 4);      // Divide into 4 brightness levels

    // Update each LED: ON if below the level threshold, OFF otherwise
    for (int i = 0; i < 4; i++) {
        digitalWrite(ledPins[i], (i < level) ? HIGH : LOW);
    }

    Serial.print("Light: ");
    Serial.print(lightValue);
    Serial.print("  Level: ");
    Serial.println(level);

    delay(100);
}
