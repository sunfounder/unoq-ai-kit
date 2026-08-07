from arduino.app_bricks.arduino_cloud import ArduinoCloud
from arduino.app_utils import App, Bridge

iot_cloud = ArduinoCloud()


def led_callback(client: object, value: bool):
    """Control the built-in LED from the Arduino Cloud switch."""
    led_state = bool(value)

    print(f"LED updated from cloud: {'ON' if led_state else 'OFF'}", flush=True)

    Bridge.call("set_led_state", led_state)


def update_environment_cloud(temperature: float, humidity: float):
    """Receive DHT11 readings from the sketch and upload them to the Cloud."""
    temperature = float(temperature)
    humidity = float(humidity)

    iot_cloud.temperature = temperature
    iot_cloud.humidity = humidity

    print(
        f"Cloud update -> Temperature: {temperature:.1f} °C, "
        f"Humidity: {humidity:.1f} %",
        flush=True,
    )


# Sensor values are written by the App and displayed in Arduino Cloud.
iot_cloud.register("temperature")
iot_cloud.register("humidity")

# The Boolean value is written from the Dashboard and controls the LED.
iot_cloud.register(
    "led",
    value=False,
    on_write=led_callback,
    interval=0.5,
)

# Allow the sketch to send temperature and humidity to Python.
Bridge.provide("update_environment_cloud", update_environment_cloud)

App.run()
