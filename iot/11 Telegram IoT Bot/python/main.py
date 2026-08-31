# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
09 Telegram IoT Bot

Commands:
  /start
  /help
  /status
  /led_on
  /led_off

The Telegram Bot token is configured in the Telegram Bot Brick,
not stored in this Python file.
"""

from arduino.app_bricks.telegram_bot import TelegramBot, Sender, Message
from arduino.app_utils import App, Bridge


bot = TelegramBot()


def start_cmd(sender: Sender, message: Message):
    """Introduce the UNO Q IoT bot."""
    sender.reply(
        f"👋 Hi {sender.first_name}! This is your Arduino UNO Q IoT Bot.\n\n"
        "Use these commands:\n"
        "/status - Check temperature, humidity, and LED status\n"
        "/led_on - Turn the external LED on\n"
        "/led_off - Turn the external LED off\n"
        "/help - Show available commands"
    )


def help_cmd(sender: Sender, message: Message):
    """Show the available bot commands."""
    sender.reply(
        "🤖 *UNO Q IoT Bot Commands:*\n\n"
        "/status - View temperature, humidity, and LED status\n"
        "/led_on - Turn the external LED on\n"
        "/led_off - Turn the external LED off\n"
        "/help - Show this help"
    )


def status_cmd(sender: Sender, message: Message):
    """Read the DHT11 and LED state through Bridge."""
    try:
        temperature = Bridge.call("get_temperature")
        humidity = Bridge.call("get_humidity")
        led_on = Bridge.call("get_led_state")

        led_text = "ON" if led_on else "OFF"

        sender.reply(
            "🌡 *UNO Q Environment Status*\n\n"
            f"Temperature: {temperature:.1f} °C\n"
            f"Humidity: {humidity:.1f} %\n"
            f"LED: {led_text}"
        )

    except Exception as exc:
        print(f"Failed to read status: {exc}", flush=True)
        sender.reply(
            "❌ I couldn't read the sensor right now. Please try again."
        )


def led_on_cmd(sender: Sender, message: Message):
    """Turn the external LED on."""
    try:
        Bridge.call("set_led", True)
        sender.reply("💡 LED turned ON.")
    except Exception as exc:
        print(f"Failed to turn LED on: {exc}", flush=True)
        sender.reply("❌ Failed to turn the LED on.")


def led_off_cmd(sender: Sender, message: Message):
    """Turn the external LED off."""
    try:
        Bridge.call("set_led", False)
        sender.reply("🌙 LED turned OFF.")
    except Exception as exc:
        print(f"Failed to turn LED off: {exc}", flush=True)
        sender.reply("❌ Failed to turn the LED off.")


bot.add_command("start", start_cmd, "Start the UNO Q IoT bot")
bot.add_command("help", help_cmd, "Show available commands")
bot.add_command("status", status_cmd, "Check environment and LED status")
bot.add_command("led_on", led_on_cmd, "Turn the external LED on")
bot.add_command("led_off", led_off_cmd, "Turn the external LED off")


print("=== Telegram IoT Bot ===", flush=True)
print("Configure the Telegram Bot Brick, run the App, then send /start.", flush=True)

App.run()
