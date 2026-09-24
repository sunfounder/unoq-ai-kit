/*
 * Measures distance and beeps faster as obstacles get closer.
 */

const int trigPin = 12;    // Trigger pin
const int echoPin = 11;    // Echo pin
const int buzzerPin = 5;   // Active buzzer

long duration;
float distanceCm;

void setup() {
    Serial.begin(115200);

    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
    pinMode(buzzerPin, OUTPUT);

    digitalWrite(trigPin, LOW);
    digitalWrite(buzzerPin, LOW);
}

float getDistance() {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);     // 10 µs trigger pulse
    digitalWrite(trigPin, LOW);

    duration = pulseIn(echoPin, HIGH, 30000);  // 30 ms timeout

    if (duration == 0) return -1;  // No echo received

    return duration * 0.0343 / 2;  // Convert to cm
}

void beepOnce(int onTime, int offTime) {
    digitalWrite(buzzerPin, HIGH);
    delay(onTime);
    digitalWrite(buzzerPin, LOW);
    delay(offTime);
}

void loop() {
    distanceCm = getDistance();

    Serial.print("Distance: ");
    if (distanceCm < 0) {
        Serial.println("Out of range");
        digitalWrite(buzzerPin, LOW);
        delay(300);
        return;
    } else {
        Serial.print(distanceCm);
        Serial.println(" cm");
    }

    if (distanceCm > 100) {
        digitalWrite(buzzerPin, LOW);  // Safe — no alarm
        delay(300);
    } else if (distanceCm > 50) {
        beepOnce(100, 500);             // Slow beep
    } else if (distanceCm > 20) {
        beepOnce(100, 250);             // Medium beep
    } else {
        beepOnce(100, 100);             // Fast urgent beep
    }
}
