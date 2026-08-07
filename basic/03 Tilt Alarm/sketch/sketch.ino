/*
 * Sounds a rhythmic alarm when the device is tilted.
 */

const int tiltPin = 2;    // Tilt switch connected to pin 2
const int buzzerPin = 5;  // Active buzzer connected to pin 5

void setup() {
    pinMode(tiltPin, INPUT_PULLUP);  // Tilt switch: closed → LOW, open → HIGH
    pinMode(buzzerPin, OUTPUT);
    digitalWrite(buzzerPin, LOW);    // Start with buzzer off
}

void loop() {
    int tiltState = digitalRead(tiltPin);

    // Tilted? (switch open → pin reads HIGH)
    if (tiltState == HIGH) {
        delay(30);  // Simple debounce: wait and re-check

        if (digitalRead(tiltPin) == HIGH) {
            // Rhythmic alarm: two short beeps, one long beep
            digitalWrite(buzzerPin, HIGH);
            delay(100);
            digitalWrite(buzzerPin, LOW);
            delay(100);

            digitalWrite(buzzerPin, HIGH);
            delay(300);
            digitalWrite(buzzerPin, LOW);
            delay(200);
        }
    } else {
        digitalWrite(buzzerPin, LOW);  // Upright → silent
    }
}
