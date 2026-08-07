/*
 * Blinks an external LED connected to pin 5.
 */

const int ledPin = 5;  // LED connected to digital pin 5

void setup() {
    pinMode(ledPin, OUTPUT);  // Set pin 5 as an output
}

void loop() {
    digitalWrite(ledPin, HIGH);  // Turn the LED on (5V)
    delay(500);                  // Wait half a second
    digitalWrite(ledPin, LOW);   // Turn the LED off (0V)
    delay(500);                  // Wait half a second
}
