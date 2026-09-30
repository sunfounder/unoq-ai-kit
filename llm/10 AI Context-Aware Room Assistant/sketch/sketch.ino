/* 10 AI Context-Aware Room Assistant
 * PIR OUT -> D4, DHT11 DATA -> D5, RGB -> D6 (R), D7 (G), D8 (B)
 */
#include <Arduino_RouterBridge.h>
#include <DHT.h>

const int PIR_PIN = 4, DHT_PIN = 5;
const int RGB_RED_PIN = 6, RGB_GREEN_PIN = 7, RGB_BLUE_PIN = 8;
DHT dht(DHT_PIN, DHT11);
float cachedTemperature = NAN, cachedHumidity = NAN;
unsigned long lastDhtRead = 0;

void setRgbPercent(int red, int green, int blue, int brightness) {
    float scale = constrain(brightness, 0, 100) / 100.0;
    analogWrite(RGB_RED_PIN, round(constrain(red, 0, 100) * 2.55 * scale));
    analogWrite(RGB_GREEN_PIN, round(constrain(green, 0, 100) * 2.55 * scale));
    analogWrite(RGB_BLUE_PIN, round(constrain(blue, 0, 100) * 2.55 * scale));
}

int set_rgb_scene(String values) {
    int a = values.indexOf(','), b = values.indexOf(',', a + 1), c = values.indexOf(',', b + 1);
    if (a < 0 || b < 0 || c < 0) return 0;
    setRgbPercent(values.substring(0, a).toInt(), values.substring(a + 1, b).toInt(),
                  values.substring(b + 1, c).toInt(), values.substring(c + 1).toInt());
    return 1;
}

String read_dht(String dummy) {
    (void)dummy;
    unsigned long now = millis();
    if (lastDhtRead == 0 || now - lastDhtRead >= 2000) {
        lastDhtRead = now;
        cachedHumidity = dht.readHumidity();
        cachedTemperature = dht.readTemperature();
    }
    if (isnan(cachedTemperature) || isnan(cachedHumidity)) return "ERROR";
    return "T=" + String(cachedTemperature, 1) + ",H=" + String(cachedHumidity, 1);
}

int read_pir(String dummy) { (void)dummy; return digitalRead(PIR_PIN) == HIGH ? 1 : 0; }

void setup() {
    pinMode(PIR_PIN, INPUT);
    pinMode(RGB_RED_PIN, OUTPUT); pinMode(RGB_GREEN_PIN, OUTPUT); pinMode(RGB_BLUE_PIN, OUTPUT);
    dht.begin(); setRgbPercent(0, 0, 0, 0); Bridge.begin();
    Bridge.provide("set_rgb_scene", set_rgb_scene);
    Bridge.provide("read_dht", read_dht); Bridge.provide("read_pir", read_pir);
}
void loop() { delay(20); }
