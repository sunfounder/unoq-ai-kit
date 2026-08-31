/*
 * Joystick Maze
 *
 * Move the joystick to guide the player through the browser maze.
 * Each joystick movement moves the player by ONE cell.
 * Return the joystick to the center before making the next move.
 *
 * Press the joystick button to restart the game.
 *
 * Joystick:
 *   X  -> A3
 *   Y  -> A2
 *   SW -> D2
 */

#include <Arduino_RouterBridge.h>

const int SW_PIN = 2;
const int X_PIN = A3;
const int Y_PIN = A2;

int xCenter = 512;
int yCenter = 512;

const int DEAD_ZONE = 150;

bool joystickReady = true;
bool lastButtonState = HIGH;

void calibrateJoystick() {
    long xTotal = 0;
    long yTotal = 0;

    for (int i = 0; i < 20; i++) {
        xTotal += analogRead(X_PIN);
        yTotal += analogRead(Y_PIN);
        delay(10);
    }

    xCenter = xTotal / 20;
    yCenter = yTotal / 20;
}

void sendMove(const char *direction) {
    Bridge.notify("joystick_move", direction);

    Serial.print("Move: ");
    Serial.println(direction);
}

void setup() {
    Serial.begin(115200);

    pinMode(SW_PIN, INPUT_PULLUP);

    Bridge.begin();

    delay(500);
    calibrateJoystick();

    Serial.println("=== Joystick Maze Ready ===");
    Serial.print("X Center: ");
    Serial.println(xCenter);
    Serial.print("Y Center: ");
    Serial.println(yCenter);
}

void loop() {
    // Joystick button: restart the game.
    bool buttonState = digitalRead(SW_PIN);

    if (lastButtonState == HIGH && buttonState == LOW) {
        Bridge.notify("reset_game");
        Serial.println("Game reset");
        delay(200);
    }

    lastButtonState = buttonState;

    int xValue = analogRead(X_PIN);
    int yValue = analogRead(Y_PIN);

    int xOffset = xValue - xCenter;
    int yOffset = yValue - yCenter;

    // Allow another move only after the joystick returns to center.
    if (abs(xOffset) < DEAD_ZONE &&
        abs(yOffset) < DEAD_ZONE) {

        joystickReady = true;
        delay(10);
        return;
    }

    if (!joystickReady) {
        delay(10);
        return;
    }

    // If moved diagonally, use the stronger axis.
    if (abs(xOffset) > abs(yOffset)) {
        if (xOffset > DEAD_ZONE) {
            sendMove("right");
            joystickReady = false;
        }
        else if (xOffset < -DEAD_ZONE) {
            sendMove("left");
            joystickReady = false;
        }
    }
    else {
        if (yOffset > DEAD_ZONE) {
            sendMove("down");
            joystickReady = false;
        }
        else if (yOffset < -DEAD_ZONE) {
            sendMove("up");
            joystickReady = false;
        }
    }

    delay(10);
}
