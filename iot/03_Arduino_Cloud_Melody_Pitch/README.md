# 03 Arduino Cloud Melody Pitch

Use a slider on an Arduino Cloud Dashboard to raise or lower the pitch of a repeating melody played by a passive buzzer.

The buzzer repeatedly plays:

```text
C4 → E4 → G4 → C5
```

The Cloud slider sends a pitch level from `0` to `50`:

```text
0  → lower-pitched melody
25 → normal-pitched melody
50 → higher-pitched melody
```

## What You'll Learn

- Connect an Arduino App Lab project to Arduino Cloud
- Create a Device, Thing, Cloud variable, and Dashboard
- Receive Cloud variable updates in Python
- Send values from Python to the Arduino sketch through Bridge
- Change the pitch of an entire melody

## Components Needed

- Arduino UNO Q
- Robot Shield
- Passive buzzer
- Jumper wires
- USB-C cable

## Wiring

Connect the passive buzzer to PWM channel **P5** on the Robot Shield.

## How to Use the Example

This example requires an Arduino Cloud account and the following Cloud resources:

```text
Device:    UNO Q AI Kit
Thing:     Melody Pitch Control
Variable:  pitch
Dashboard: Melody Pitch Dashboard
Widget:    Pitch
```

The same **UNO Q AI Kit** Device can be reused in later Arduino Cloud lessons. Create a new Thing and Dashboard for each project to keep the examples separate and easy to manage.

### Setting Up Arduino Cloud

#### Create the Device

1. Go to [Arduino Cloud](https://app.arduino.cc/) and sign in or create an account.
2. Open the **Devices** page.
3. Click **Add Device**.
4. Select **Manual Device**.
5. Select **Arduino UNO Q**.
6. Name the Device:

   ```text
   UNO Q AI Kit
   ```

7. Complete the setup and save the following credentials:

   - **Device ID**
   - **Secret Key**

   Keep the Secret Key in a safe place. Arduino Cloud may only display it once.

> **Screenshot suggestion:** Show the **Add Device** entry point and the page containing the Device ID and Secret Key.

#### Create the Thing

1. Open the **Things** page.
2. Click **Create Thing**.
3. Name the Thing:

   ```text
   Melody Pitch Control
   ```

4. Associate the Thing with the **UNO Q AI Kit** Device.

> **Screenshot suggestion:** Show the **Create Thing** entry point and the completed Thing page with the associated Device.

#### Create the Cloud Variable

Inside the Thing, click **Add Variable** and configure it as follows:

| Setting | Value |
|---|---|
| Name | `pitch` |
| Type | Integer |
| Permission | Read & Write |
| Update Policy | On change |

The variable name must be exactly:

```text
pitch
```

It must match the name registered in `python/main.py`:

```python
iot_cloud.register(
    "pitch",
    value=25,
    on_write=pitch_callback,
)
```

> **Screenshot suggestion:** Show the complete variable settings before clicking **Add Variable**.

#### Create the Dashboard

1. Open the **Dashboards** page.
2. Click **Build Dashboard**.
3. Name the Dashboard:

   ```text
   Melody Pitch Dashboard
   ```

4. Open the Dashboard in **Edit** mode.
5. Add a **Slider** widget.
6. Link the Slider to the `pitch` variable.
7. Name the widget:

   ```text
   Pitch
   ```

Keep the Slider's default range:

```text
0–50
```

No custom minimum or maximum values are required.

> **Screenshot suggestion:** Show the **Build Dashboard** entry point, the variable-linking page, and the completed Slider widget.

### Configure the Arduino Cloud Brick

1. Import this ZIP file into **Arduino App Lab**.
2. Open the App.
3. Click the **Arduino Cloud** Brick.
4. Click **Brick Configuration**.
5. Enter the credentials saved when creating the Device:

   ```text
   ARDUINO_DEVICE_ID: your Device ID
   ARDUINO_SECRET: your Secret Key
   ```

6. Save the Brick configuration.

> **Screenshot suggestion:** Show where to open **Brick Configuration** and where to enter the two credentials.

### Launch the App

1. Click **Run** (▶) in Arduino App Lab.
2. Wait for the App and sketch to start.
3. Open the Arduino Cloud Dashboard.
4. Move the **Pitch** slider.

The buzzer continues playing the same melody, but its overall pitch changes:

```text
Move left  → lower pitch
Move right → higher pitch
```

## How It Works

### Cloud Variable Callback

The Arduino Cloud Brick calls `pitch_callback()` whenever the `pitch` variable changes:

```python
def pitch_callback(client: object, value: int):
    pitch_level = max(0, min(50, int(value)))

    print(f"Pitch level: {pitch_level}", flush=True)

    Bridge.call("set_pitch_level", pitch_level)
```

Python limits the value to the valid Slider range and sends it to the Arduino sketch through Bridge.

### Melody Pitch Mapping

The sketch maps the pitch level from `0–50` to `50%–200%`:

```cpp
int pitchPercent = map(
    pitchLevel,
    0,
    50,
    50,
    200
);
```

The four base notes are:

```cpp
const uint16_t MELODY[] = {
    262,  // C4
    330,  // E4
    392,  // G4
    523   // C5
};
```

Each note is multiplied by the current pitch percentage:

```cpp
uint16_t frequency =
    MELODY[currentNote] * pitchPercent / 100;
```

For example, the base note C4 is `262 Hz`:

```text
Pitch level 0  → 50%  → 131 Hz
Pitch level 25 → 125% → 327 Hz
Pitch level 50 → 200% → 524 Hz
```

The relative spacing between the notes stays the same, so the melody remains recognizable while becoming lower or higher.

## Expected Output

The Python Console displays the Cloud value:

```text
Pitch level: 8
Pitch level: 21
Pitch level: 37
Pitch level: 50
```

The Serial Monitor displays the frequency of each note:

```text
Cloud-controlled melody is ready.
Pitch level: 25
Note frequency: 327 Hz
Note frequency: 412 Hz
Note frequency: 490 Hz
Note frequency: 653 Hz
```

## Troubleshooting

### The App does not receive Slider updates

Check that:

- The Dashboard Slider is linked to the correct `pitch` variable.
- The variable is named exactly `pitch`.
- Its type is **Integer**.
- Its permission is **Read & Write**.
- Its update policy is **On change**.
- The Thing is associated with the same Device used in Brick Configuration.
- The Device ID and Secret Key are correct.

### The buzzer plays, but its pitch does not change

Open the Python Console and move the Slider. You should see different values:

```text
Pitch level: 5
Pitch level: 18
Pitch level: 42
```

If the value changes in the Console but the sound does not change, check that the passive buzzer is connected to **P5** and that the sketch is running.

### The Slider changes slowly after startup

The initial Arduino Cloud connection may take some time. After the App connects successfully, later Slider updates should arrive more quickly.
