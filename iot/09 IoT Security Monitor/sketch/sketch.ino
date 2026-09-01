/*
 * 08 IoT Security Monitor
 *
 * PIR motion sensor -> D2
 * Passive buzzer    -> D5
 */

#include <Arduino_RouterBridge.h>

const int PIR_PIN = 2;
const int BUZZER_PIN = 5;

// Keep the alarm latched for 10 s after the last motion trigger.
const unsigned long MOTION_HOLD_TIME = 10000;

// Two-tone siren: alternate between 800 Hz and 1200 Hz every 300 ms.
const int ALARM_LOW_FREQ = 800;
const int ALARM_HIGH_FREQ = 1200;
const unsigned long ALARM_TONE_TIME = 300;

bool motionActive = false;
bool highTone = false;

unsigned long lastMotionTime = 0;
unsigned long lastToneChange = 0;

void setMotionState(bool active)
{
    motionActive = active;

    if (active)
    {
        highTone = false;
        tone(BUZZER_PIN, ALARM_LOW_FREQ);
        lastToneChange = millis();
    }
    else
    {
        noTone(BUZZER_PIN);
    }

    // Notify Python so it can take snapshots while motion is active.
    Bridge.notify("motion_state", active);

    Serial.print("Security state: ");
    Serial.println(active ? "MOTION DETECTED" : "AREA CLEAR");

    Serial.print("Alarm: ");
    Serial.println(active ? "ON" : "OFF");
}

void updateAlarm()
{
    if (!motionActive)
    {
        return;
    }

    unsigned long now = millis();

    if (now - lastToneChange >= ALARM_TONE_TIME)
    {
        // Swap between the high and low siren tones.
        highTone = !highTone;

        tone(
            BUZZER_PIN,
            highTone ? ALARM_HIGH_FREQ : ALARM_LOW_FREQ
        );

        lastToneChange = now;
    }
}

void setup()
{
    Serial.begin(115200);

    pinMode(PIR_PIN, INPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    noTone(BUZZER_PIN);

    Bridge.begin();

    Serial.println("=== IoT Security Monitor ===");
    Serial.println("PIR: D2");
    Serial.println("Passive buzzer: D5");
    Serial.println("Motion hold: 10 seconds");
    Serial.println("Monitoring...");
}

void loop()
{
    unsigned long now = millis();
    bool pirDetected = digitalRead(PIR_PIN) == HIGH;

    // Any motion restarts the hold timer and raises the alarm.
    if (pirDetected)
    {
        lastMotionTime = now;

        if (!motionActive)
        {
            setMotionState(true);
        }
    }

    // No motion for the hold time -> clear the alarm.
    if (
        motionActive &&
        !pirDetected &&
        now - lastMotionTime >= MOTION_HOLD_TIME
    )
    {
        setMotionState(false);
    }

    updateAlarm();

    delay(20);
}
