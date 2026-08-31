"""Read a DHT11 sensor and announce the values every 30 seconds."""

import time

from arduino.app_utils import Bridge

from sunfounder_tts import EdgeTTS


WEATHER_RPC = "read_weather"
ANNOUNCEMENT_INTERVAL = 30


tts = EdgeTTS()
tts.set_voice("en-US-JennyNeural")
tts.set_volume(50)

print("Dynamic TTS Weather Reporter")
print("The temperature and humidity will be announced every 30 seconds.")

try:
    while True:
        sensor_data = str(Bridge.call(WEATHER_RPC, "")).strip()

        if sensor_data == "error":
            print("Failed to read from the DHT11 sensor.")
        else:
            try:
                temperature_text, humidity_text = sensor_data.split(",", 1)
                temperature = float(temperature_text)
                humidity = float(humidity_text)

                message = (
                    f"The temperature is {temperature:.1f} degrees Celsius. "
                    f"The humidity is {humidity:.1f} percent."
                )

                print(
                    f"Temperature: {temperature:.1f} °C | "
                    f"Humidity: {humidity:.1f} %"
                )
                print(f"Speaking: {message}")

                tts.say(message)

            except (TypeError, ValueError):
                print(f"Unexpected sensor data: {sensor_data}")

        time.sleep(ANNOUNCEMENT_INTERVAL)

except KeyboardInterrupt:
    print("\nProgram stopped.")
