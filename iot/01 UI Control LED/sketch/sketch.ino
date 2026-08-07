// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

#include <Arduino_RouterBridge.h>

const int ledPin = 5;

void setup() {
    Monitor.begin();
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW);
  
    Bridge.begin();
    Bridge.provide("set_led_state", set_led_state);
}

void loop() {}

void set_led_state(bool state) {
    // LOW state means LED is ON
    digitalWrite(ledPin, state ? HIGH : LOW);
}

