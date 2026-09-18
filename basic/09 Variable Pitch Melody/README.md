# 09 Variable Pitch Melody

Turn a potentiometer to raise or lower the pitch of a repeating four-note melody (C4 → E4 → G4 → C5). The passive buzzer plays the notes in sequence, and the potentiometer shifts the entire melody up or down while keeping the musical intervals intact — turn left for deeper, right for higher.

## Hardware

- Pan Tilt Kit ×1
- Breadboard ×1
- Potentiometer ×1
- Passive buzzer ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the potentiometer to A2 and the passive buzzer to D5.

![Wiring Diagram](assets/docs_assets/wiring_pot_buzzer.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [09 Variable Pitch Melody.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/09.Variable.Pitch.Melody.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. Turn the potentiometer while the melody plays — the pitch shifts up or down. Open the Serial Monitor to see the current frequency.

## How it Works

**Flow**

- `setup()` — configures the buzzer pin as `OUTPUT` and silences it with `noTone()`
- `loop()` — plays the four notes in sequence, reading the potentiometer before each note and multiplying the base frequency by the pitch percentage

**The melody array**

`MELODY[]` stores four base frequencies: C4 (262 Hz), E4 (330 Hz), G4 (392 Hz), C5 (523 Hz). The sketch loops through them continuously — `for (int note = 0; note < MELODY_LENGTH; note++)`.

**Pitch control**

`map(potValue, 0, 1023, 50, 200)` converts the potentiometer reading to a pitch percentage from 50% to 200%. Each base note is multiplied by this percentage — `MELODY[note] * pitchPercent / 100` — so at center position (~125%) the melody plays a little high, at minimum (50%) it plays an octave lower, at maximum (200%) an octave higher. The ratios between notes stay the same, so the melody is recognizable at any pitch.

**Generating the tone**

`playFrequency()` calls `tone(BUZZER_PIN, frequency)` — Arduino generates a 50% duty-cycle square wave at that frequency, and the passive buzzer vibrates to produce the note. `stopBuzzer()` calls `noTone(BUZZER_PIN)` to silence the buzzer between notes so they don't blur together.

**Same buzzer, same pin as the PIR alarm**

The PIR Motion Alarm lesson also drove a passive buzzer on D5 with `tone()` — this lesson reuses the exact same approach. The only new part here is the melody: an array of frequencies plus a `for` loop, and the potentiometer shifting the whole tune.
