# 05 PIR Motion Alarm

Detect motion with a PIR (Passive Infrared) sensor and sound a passive buzzer alarm — like a simple home security system. The PIR sensor detects changes in infrared heat radiation, making it ideal for sensing people and animals moving through its field of view.

## Hardware

- Pan Tilt Kit ×1
- Breadboard ×1
- PIR motion sensor module ×1
- Passive buzzer ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the PIR sensor's VCC to 3.3V, OUT to D4, GND to GND, and the passive buzzer to D5.

![Wiring Diagram](assets/docs_assets/wiring_pc_buzzer_pir.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `05 PIR Motion Alarm.zip` from `unoq-ai-kit\basic`.
4. Click **Run**.
5. Wait 30 seconds for the PIR sensor to warm up (the Serial Monitor shows "PIR Motion Alarm — warming up (30 seconds)..."). Once it says "Ready!", wave your hand or walk in front of the sensor — the buzzer sounds a two-tone siren (alternating 800 Hz and 1200 Hz). Stay still and the alarm stops.

## How it Works

**Flow**

- `setup()` — configures the PIR pin as `INPUT`, the buzzer pin as `OUTPUT`, calls `noTone()` to ensure the buzzer starts silent, then waits 30 seconds for the PIR sensor to stabilize
- `loop()` — reads the PIR sensor; if motion is detected, calls `tone()` four times alternating 800 Hz and 1200 Hz; if not, calls `noTone()` to keep the buzzer off

**The PIR sensor**

The PIR sensor has three pins: VCC (5 V), GND, and OUT. When it detects a change in infrared radiation — like a person walking by — the OUT pin goes HIGH. When the area is still, OUT stays LOW. Reading it is just `digitalRead(pirPin)` — the same as reading a button.

**The 30-second warm-up**

PIR sensors need time to calibrate to the background infrared environment when first powered on. During this period the output may trigger randomly, so `delay(30000)` in `setup()` ignores it. The Serial Monitor prints a message so you know what's happening.

**Driving the passive buzzer with tone()**

Unlike an active buzzer (just HIGH/LOW with `digitalWrite()`), a passive buzzer needs a frequency-controlled square wave. The Arduino `tone(pin, frequency)` function generates a 50% duty-cycle square wave at the specified pin and frequency — the passive buzzer turns that oscillation into audible sound. `noTone(pin)` stops the signal and silences the buzzer.

**The two-tone siren**

Alternating 800 Hz and 1200 Hz creates a classic warning siren — the frequency change grabs attention better than a single steady tone. Each `tone()` call plays for 250 ms, and a 500 ms pause after the siren prevents a single motion event from retriggering immediately.

**Passive vs active buzzer**

Active buzzers have a built-in oscillator — apply DC voltage and they beep at a fixed frequency, controlled with `digitalWrite()`. Passive buzzers have no internal oscillator — you must supply an AC signal at the desired frequency, which `tone()` generates for you. This gives you control over pitch, so you can create sirens, melodies, and sound effects instead of just beeps.
