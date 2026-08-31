const int pirPin = 2;     // PIR sensor OUT connected to D2
const int buzzerPin = 5;  // Passive buzzer connected to D5

void setup() {
    pinMode(pirPin, INPUT);
    pinMode(buzzerPin, OUTPUT);
    noTone(buzzerPin);

    Serial.begin(115200);
    Serial.println("PIR Motion Alarm — warming up (30 seconds)...");
    delay(30000);  // PIR sensor warm-up period
    Serial.println("Ready! Move in front of the sensor.");
}

void loop() {
    int motion = digitalRead(pirPin);

    if (motion == HIGH) {
        Serial.println("Motion detected!");

        // Alternate between two tones to create a warning sound
        tone(buzzerPin, 800);
        delay(250);

        tone(buzzerPin, 1200);
        delay(250);

        tone(buzzerPin, 800);
        delay(250);

        tone(buzzerPin, 1200);
        delay(250);

        noTone(buzzerPin);

        delay(500);  // Pause before checking again
    } else {
        noTone(buzzerPin);  // No motion → silent
    }
}
