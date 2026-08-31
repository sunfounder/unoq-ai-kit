/*
 * Variable Pitch Melody
 *
 * Turn the potentiometer to raise or lower the pitch of the whole melody.
 *
 * Potentiometer: A2
 * Passive buzzer: D5 (driven with tone())
 */

const int POT_PIN = A2;
const int BUZZER_PIN = 5;

const int MIN_PITCH_PERCENT = 50;
const int MAX_PITCH_PERCENT = 200;

const int NOTE_DURATION = 250;
const int NOTE_GAP = 50;

const uint16_t MELODY[] = {
    262,  // C4
    330,  // E4
    392,  // G4
    523   // C5
};

const int MELODY_LENGTH = sizeof(MELODY) / sizeof(MELODY[0]);

void playFrequency(uint16_t frequency)
{
    tone(BUZZER_PIN, frequency);
}

void stopBuzzer()
{
    noTone(BUZZER_PIN);
}

void setup()
{
    Serial.begin(115200);

    pinMode(BUZZER_PIN, OUTPUT);
    noTone(BUZZER_PIN);

    Serial.println("=== Variable Pitch Melody ===");
    Serial.println("Turn the potentiometer to change the melody pitch.");
}

void loop()
{
    for (int note = 0; note < MELODY_LENGTH; note++)
    {
        int potValue = analogRead(POT_PIN);

        int pitchPercent = map(
            potValue,
            0,
            1023,
            MIN_PITCH_PERCENT,
            MAX_PITCH_PERCENT
        );

        uint16_t frequency =
            (uint32_t)MELODY[note] * pitchPercent / 100;

        playFrequency(frequency);

        Serial.print("Potentiometer: ");
        Serial.print(potValue);
        Serial.print("    Pitch: ");
        Serial.print(pitchPercent);
        Serial.print("%    Note frequency: ");
        Serial.print(frequency);
        Serial.println(" Hz");

        delay(NOTE_DURATION);

        stopBuzzer();
        delay(NOTE_GAP);
    }
}
