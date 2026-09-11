/*
 * Press the button to turn on the LED.
 */

const int buttonPin = 4;  // Button connected to pin 4
const int ledPin = 5;     // LED connected to pin 5

void setup() {
    pinMode(buttonPin, INPUT_PULLUP);  // Pin 4 reads input with pull-up
    pinMode(ledPin, OUTPUT);           // Pin 5 controls the LED
}

void loop() {
    int buttonState = digitalRead(buttonPin);

    // Button pressed → LOW (connected to GND)
    if (buttonState == LOW) {
        digitalWrite(ledPin, HIGH);  // Turn LED ON
    } else {
        digitalWrite(ledPin, LOW);   // Turn LED OFF
    }
}
