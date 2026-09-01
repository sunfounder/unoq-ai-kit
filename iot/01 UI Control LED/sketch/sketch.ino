// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

// Controls an LED via RPC calls from the Python app.
// LED on D5; the Bridge exposes set_led_state() to Python.
//
#include <Arduino_RouterBridge.h>

const int ledPin = 5;

void setup() {
    Monitor.begin();
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW);
  
    Bridge.begin();
    // Register the RPC function so Python can call it.
    Bridge.provide("set_led_state", set_led_state);
}

void loop() {}

void set_led_state(bool state) {
    // LOW state means LED is ON
    digitalWrite(ledPin, state ? HIGH : LOW);
}

