/*
 * Cloud-Controlled Melody Pitch
 *
 * The Arduino Cloud slider sends a pitch level from 0 to 50.
 * The program maps this value to 50%–200% of the original melody pitch.
 *
 * Connect the passive buzzer to PWM channel P5 on the Robot Shield.
 */

#include <Arduino_RouterBridge.h>
#include "RobotShield.h"

const int MIN_PITCH_LEVEL = 0;
const int MAX_PITCH_LEVEL = 50;

const int MIN_PITCH_PERCENT = 50;
const int MAX_PITCH_PERCENT = 200;

const int NOTE_DURATION = 250;
const int NOTE_GAP = 50;

Pwm buzzer(5);

const uint16_t MELODY[] = {
    262,  // C4
    330,  // E4
    392,  // G4
    523   // C5
};

const int MELODY_LENGTH = sizeof(MELODY) / sizeof(MELODY[0]);

volatile int pitchLevel = 25;

int currentNote = 0;
unsigned long noteStartTime = 0;
bool notePlaying = false;


void playFrequency(uint16_t frequency)
{
    uint32_t period = 1000000UL / frequency;
    uint16_t pulse = period / 2;

    buzzer.setEnable(false);
    buzzer.setFreq(frequency);
    buzzer.setPulse(pulse);
    buzzer.setEnable(true);
}


void stopBuzzer()
{
    buzzer.setEnable(false);
}


void setPitchLevel(int value)
{
    pitchLevel = constrain(
        value,
        MIN_PITCH_LEVEL,
        MAX_PITCH_LEVEL
    );

    Serial.print("Pitch level: ");
    Serial.println(pitchLevel);
}


void setup()
{
    Serial.begin(115200);

    I2cBus::i2c().begin();

    buzzer.begin();
    buzzer.setEnable(false);

    Bridge.begin();
    Bridge.provide("set_pitch_level", setPitchLevel);

    Serial.println("Cloud-controlled melody is ready.");
}


void loop()
{
    unsigned long now = millis();

    if (!notePlaying)
    {
        int pitchPercent = map(
            pitchLevel,
            MIN_PITCH_LEVEL,
            MAX_PITCH_LEVEL,
            MIN_PITCH_PERCENT,
            MAX_PITCH_PERCENT
        );

        uint16_t frequency =
            MELODY[currentNote] * pitchPercent / 100;

        playFrequency(frequency);

        Serial.print("Note frequency: ");
        Serial.print(frequency);
        Serial.println(" Hz");

        noteStartTime = now;
        notePlaying = true;
    }

    if (notePlaying && now - noteStartTime >= NOTE_DURATION)
    {
        stopBuzzer();
        noteStartTime = now;
        notePlaying = false;

        currentNote++;

        if (currentNote >= MELODY_LENGTH)
        {
            currentNote = 0;
        }

        delay(NOTE_GAP);
    }
}