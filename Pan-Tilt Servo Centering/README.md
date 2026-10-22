# Pan-Tilt Servo Centering

Hold both pan-tilt servos at 90 degrees while assembling the pan-tilt kit.

## Libraries Used

- **Arduino_HardwareServo** library

## Wiring

Connect the servos to the Robot Shield, matching the signal, power, and ground pins:

- **Pan servo → D9**
- **Tilt servo → D10**

## How to Use

1. Import this ZIP into Arduino App Lab.
2. Connect both servos to the Robot Shield as described above.
3. Connect the UNO Q to your computer using a USB-C cable.
4. Click **Run** and wait for both servos to reach 90 degrees.
5. Fit the servo horns in the positions specified by the pan-tilt assembly instructions. Keep the app running so the servos hold their center positions.

## How It Works

- `setup()` attaches the pan servo to D9 and the tilt servo to D10.
- `loop()` sends a 90-degree command to both servos every 100 ms.

The servos remain at 90 degrees instead of sweeping back and forth. No joystick or reset button is required.

