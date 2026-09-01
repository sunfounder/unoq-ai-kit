// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

// Controls an RGB LED via RPC calls from the Python app.
// Colors on RobotShield PWM channels: red P6, green P5, blue P4.
//
#include <Arduino_RouterBridge.h>
#include "RobotShield.h"

// RGB LED connected to RobotShield PWM channels
Pwm red(6);    // Red   — P6
Pwm green(5);  // Green — P5
Pwm blue(4);   // Blue  — P4

void setup() {
    Monitor.begin();

    // Initialize I2C bus for RobotShield
    I2cBus::i2c().begin();

    // Set up PWM channels
    red.begin();
    green.begin();
    blue.begin();

    red.setFreq(1000);
    green.setFreq(1000);
    blue.setFreq(1000);

    red.setEnable(true);
    green.setEnable(true);
    blue.setEnable(true);

    // Initialize Bridge and register RPC
    Bridge.begin();
    Bridge.provide("set_rgb_color", set_rgb_color);
}

void loop() {
    // Empty — everything is event-driven via Bridge
}

// Set RGB LED color
// r, g, b: 0–255 (web standard), mapped to 0–1000 (RobotShield PWM)
void set_rgb_color(int r, int g, int b) {
    red.setPulse(map(r, 0, 255, 0, 1000));
    green.setPulse(map(g, 0, 255, 0, 1000));
    blue.setPulse(map(b, 0, 255, 0, 1000));
}
