.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

08 AI Smart Guard
=================

You've watched your camera detect faces, track them, and speak — now it's time to give it a job. In this lesson you'll build the **AI Smart Guard**: a complete security sentry that patrols the room by sweeping its camera back and forth, and the moment it spots an intruder — a whole **person**, not just a face — it turns red, screams an alarm, and announces the intruder out loud. When the coast is clear, it settles back into green, silent patrol. It is the largest vision project in this module: detection, motion, light, sound, and voice, all fused into one autonomous system.

.. image:: img/08_ai_smart_guard.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Detect **people** (full bodies) with a general object-detection model — not just faces
* Build a two-state system — **patrolling** and **alarming** — shared across Python and the sketch
* Coordinate three outputs at once: servo scanning, an RGB LED, and a buzzer
* Rate-limit spoken alerts so the guard warns without nagging
* Auto-recover: return to patrol after the intruder has been gone for 3 seconds

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_rgb_led` (common cathode)
   * - 3 * :ref:`cpn_resistor` (220Ω)
     - 1 * :ref:`cpn_buzzer` (active)
   * - |list_pan_tilt|
     - |list_rgb_led|
   * - |list_220ohm|
     - |list_active_buzzer|

**Software Requirements**

This project uses the following Bricks and sketch library:

* Bricks (declared in ``app.yaml``):
  * ``video_object_detection`` — runs the **general object-detection** model on every camera frame
  * ``web_ui`` — serves the Web UI with the live camera feed and guard status
  * ``sunfounder_tts`` — text-to-speech for the voice alerts (EdgeTTS)
* Libraries (declared in ``sketch.yaml``):
  * ``Arduino_HardwareServo`` (0.0.1) — drives the servos with hardware PWM

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

Wire the RGB LED with the same layout as the color mixing project earlier: the **common cathode** (the longest leg) goes to **GND**, and the red, green, and blue anodes go to **D8**, **D7**, and **D6** — each through its own 220Ω resistor. The active buzzer's **+** leg goes to **D5** and its **−** leg to **GND**. The pan and tilt servos plug straight into **D9** and **D10** on the Robot Shield's servo headers; they need no breadboard wiring.

.. image:: /img/wiring/wiring_smart_guard.png
   :width: 600
   :align: center

**Person Detection vs. Face Detection**

Why does the guard watch for whole people instead of faces? Because the two jobs need two different models. The **face-detection** model you used earlier only fires on a clear view of a face — eyes, nose, and mouth. The **general object-detection** model this project uses reports a "person" class for a full body, so it still works when someone faces away, wears a mask or sunglasses, or is partly hidden. A greeter wants faces; a guard wants intruders — and an intruder usually doesn't cooperate by facing the camera.

2. Run the App
----------------

#. Download :download:`08 AI Smart Guard.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/08.AI.Smart.Guard.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. The app appears in **Apps** — click it to open.

#. The pan-tilt servos draw more power than the USB port alone can provide, so connect the battery pack to the Robot Shield.

#. Click the **Run** button (▶). The RGB LED glows **green** and the pan servo starts sweeping slowly from side to side like a watchman. The sketch prints its banner, ``=== AI Smart Guard Ready ===``, over the serial connection, and the Console shows ``🛡️  AI Smart Guard is running.`` followed by ``🔊 TTS ready.`` once the speech engine is up.

#. Open the **Web UI** tab. The live camera feed fills the page, and the guard panel shows a green dot — **All clear — scanning** — with the note "AI Smart Guard protecting the perimeter."

#. Walk in front of the camera. The guard snaps to **red**, the buzzer starts beeping, the scanning stops, and you hear the voice alert: *"Intruder detected. Intruder detected."* The Web UI switches to the red alert panel: **🚨 Intruder detected! (100%)**.

#. Step out of view and count to four. After about 3 seconds without seeing you, the guard returns to **green**, the buzzer falls silent, the servo resumes its patrol sweep, and the speaker announces *"All clear."*

.. image:: img/08_ai_smart_guard.png
   :width: 600
   :align: center

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

**How it Works**

Now that you've seen the guard react, here is how the two processors share the job: the whole system is two states — **patrolling** and **alarming** — decided in Python and executed in the sketch.

An App Lab project is a folder containing multiple files. Here's what each one does:

* ``08 AI Smart Guard/`` — the app folder

  * ``app.yaml`` — App metadata: declares the ``video_object_detection``, ``web_ui``, and ``sunfounder_tts`` bricks

  * ``python/``

    * ``main.py`` — Person detection, the alarm decisions, and the voice alerts

  * ``sketch/``

    * ``sketch.yaml`` — Sketch configuration (declares the ``Arduino_HardwareServo`` library)
    * ``sketch.ino`` — Servo sweep, RGB status, and the buzzer alarm on the microcontroller

  * ``assets/``

    * ``index.html`` — Web UI structure (camera frame, guard panel, status row)
    * ``app.js`` — Browser logic: camera stream and Socket.IO events
    * ``style.css`` — Visual styling
    * ``libs/`` — JavaScript libraries (Socket.IO)
    * ``img/`` — Static resources

  * ``README.md`` — Project documentation and usage guide

The data path from a person walking into the frame to the alarm — and back:

.. mermaid::

   sequenceDiagram
       participant C as Camera (CSI)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)
       participant B as Browser (HTML/JS)

       C->>P: frame (flipped vertically)
       S->>S: pan servo sweeps 45°–135°, 1° every 40 ms
       P->>P: VideoObjectDetection → on_detect("person")
       P->>S: Bridge.call("alarm_on")
       S->>S: RGB red, buzzer beeps every 150 ms, sweep stops
       P->>P: EdgeTTS speaks "Intruder detected." — at most once per 8 s
       P-->>B: guard_status {alert: true, confidence: 100}
       P->>S: Bridge.call("alarm_off") — no person for 3 s
       S->>S: RGB green, buzzer off, sweep resumes
       P-->>B: guard_status {alert: false}

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``loop()`` sweeps the pan servo one degree every 40 ms (``scanInterval``) between 45° and 135°, reversing at each end; the tilt servo holds its 90° center
  * ``alarm_on()`` sets ``alarming = true`` and ``scanning = false``, then paints the LED red with ``setRgb()`` — ``analogWrite()`` on **D8** (red), **D7** (green), and **D6** (blue)
  * While alarming, ``loop()`` toggles the buzzer on **D5** every 150 ms — a beep-beep-beep alarm with no blocking ``delay()``
  * ``alarm_off()`` silences the buzzer, returns the RGB LED to green, and lets the sweep resume
  * ``Bridge.provide("alarm_on", alarm_on)`` and ``Bridge.provide("alarm_off", alarm_off)`` expose both commands, and each one ignores a repeated call

**Python (main.py)** — runs on the Linux MPU
  * ``Camera(adjustments=lambda frame: frame[::-1, :])`` flips every frame vertically, because the CSI camera is mounted upside down on the carrier
  * ``VideoObjectDetection(camera, confidence=0.4, debounce_sec=0.5)`` runs the **general object-detection** model — this time with no ``model:`` restriction, so it reports all of its classes
  * ``detection.on_detect("person", person_detected)`` subscribes to the ``person`` class only
  * ``person_detected()`` refreshes ``last_intruder_time`` and, on the first sighting, calls ``Bridge.call("alarm_on")``
  * ``speak()`` queues the alert for EdgeTTS, which runs in its own daemon thread, and ``last_spoke_alert`` throttles it to once every 8 seconds
  * ``ui.send_message("guard_status", …)`` sends the red or green panel state to the browser
  * ``monitor_guard()`` checks the clock every 0.2 s and, after ``LOST_TIMEOUT = 3.0`` seconds with no person, calls ``Bridge.call("alarm_off")`` and speaks "All clear."
  * ``App.run()`` starts the app

**Bridge** — communication channel between MPU and MCU
  * Python side: ``Bridge.call("alarm_on")`` and ``Bridge.call("alarm_off")``
  * Sketch side: ``Bridge.provide("alarm_on", alarm_on)`` and ``Bridge.provide("alarm_off", alarm_off)``
  * Only two short commands ever cross the Bridge — the pins, the sweep speed, and the beep timing all stay in the sketch

**Browser (HTML/JS)** — runs in the user's browser
  * The camera feed is an ``<iframe>`` pointed at the stream URL on port 4912 (``/embed``), reloaded once a second until it loads
  * ``socket.on("guard_status", …)`` swaps the panel between the green **All clear — scanning** state and the red **🚨 Intruder detected! (100%)** alert
  * ``socket.on("disconnect")`` flips the dot red and shows **Connection lost**

**The RGB LED is the guard's status lamp** — Green means *patrolling — all clear*; red means *intruder!* Because the LED is common cathode, a channel lights when its pin goes high, so full brightness is 255. The buzzer on **D5** is an *active* buzzer — it generates its own tone, so the sketch only has to switch its power on and off.

**Why throttle the voice?** — Speaking takes seconds and the intruder usually stays in view, so announcing every detection would leave the speaker screaming continuously. The ``last_spoke_alert`` timestamp limits the alert to **once every 8 seconds**, however many detections arrive. The sentence repeats "Intruder detected" on purpose, so it stays audible over the buzzer.

**All clear, automatically** — A background monitor thread checks every 0.2 s whether any person detection has refreshed ``last_intruder_time`` within the last 3 seconds. Once the intruder leaves — or hides long enough — the thread flips the state back: ``Bridge.call("alarm_off")``, a spoken *"All clear."*, and the Web UI's green panel. The guard is then ready for its next intruder — no button, no human in the loop.

3. Experiment
----------------

**Test the Guard**

Try each of these scenarios with the app running and watch the whole system respond:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - What you do
     - What the system does
   * - Walk into the camera's view
     - RGB turns red, buzzer beeps, servo freezes, voice alert plays, Web UI shows the red alert panel
   * - Keep moving around in front of the camera
     - Stays red and beeping; the voice repeats at most once every 8 seconds
   * - Leave the view and stay away
     - After 3 seconds: green LED, silent buzzer, scanning resumes, "All clear." is spoken
   * - Walk in with your **back** to the camera
     - Still triggers — person detection sees full bodies, not just faces
   * - Put a coat or backpack on a chair in view
     - May trigger — person-shaped objects can fool the model (that's what the next experiment is about)

**Challenge: Reduce False Alarms**

Hang a coat on a chair and place it in the camera's view. Does the guard raise an alarm on it? The sensitivity lives in one number in ``main.py``: ``confidence=0.4``. Try raising it to ``0.6`` and then ``0.8`` — run the app after each change and test both the coat and a real person walking by. Find the lowest confidence value where the coat stops triggering while a real person still does. What's the trade-off you're making at each threshold?

**Challenge: Test the Recovery Time**

Have a friend walk through the frame and keep walking until they're out of view. Time the gap between them disappearing and the buzzer stopping — is it really about 3 seconds? The timer lives in ``LOST_TIMEOUT = 3.0``. Try setting it to ``10.0`` and think about which is better for a real security system: a guard that stands down quickly after a false alarm, or one that stays alert a little longer?

4. Troubleshooting
--------------------

**The RGB LED colors are wrong (or nothing lights up)**

* **Cause:** Channels are swapped, a resistor is missing, or the common cathode isn't grounded.
* **Solution:** Check the wiring: red anode → **D8**, green anode → **D7**, blue anode → **D6**, each through its own 220Ω resistor, and the longest leg (common cathode) → **GND**. Never connect an RGB channel to a pin without its resistor — it burns out the LED.

**The buzzer doesn't sound during an alarm**

* **Cause:** The buzzer legs are reversed, or it's a passive buzzer.
* **Solution:** Connect the buzzer's **+** leg to **D5** and **−** leg to **GND**. This project needs an *active* buzzer — it beeps by itself when powered. A passive buzzer needs a tone signal to make any sound at all.

**The guard raises false alarms on empty rooms**

* **Cause:** The model sees person-like shapes — coats, shadows, curtains moving in a draft — and the 0.4 confidence threshold is generous on purpose.
* **Solution:** Raise ``confidence=0.4`` in ``main.py`` to ``0.6`` or ``0.7`` and re-run. Point the camera away from windows and doors where shadows move. You can also increase ``debounce_sec`` so the model must agree over a longer time before a detection counts.

**The guard never triggers, even when someone walks by**

* **Cause:** The person is too far away or too dimly lit, or the servo sweep aims the camera at the wrong area at the wrong moment.
* **Solution:** Stay within 1–3 meters of the camera and keep the room reasonably lit. Remember the camera *scans* — an intruder who crosses while the camera is aimed the other way is simply not in the frame yet. Test by standing still in view for a moment while the sweep passes over you.

**The servos don't sweep after an alarm ends**

* **Cause:** The battery is weak, or the pan servo plug has worked loose.
* **Solution:** Connect (or recharge) the battery pack — the sweep keeps drawing power continuously. Check that the pan servo is firmly plugged into **D9** with the cable's brown wire toward the outside edge of the header.

**No voice alerts, though the lights and buzzer work**

* **Cause:** The TTS runtime is still being prepared, or the board has no Internet access.
* **Solution:** The first TTS run can take half an hour to download dependencies — watch the Console for ``🔊 TTS ready.`` before expecting speech. EdgeTTS synthesizes audio online, so keep the UNO Q connected to the Internet.

5. Summary
-------------

You just built a fully autonomous security guard — it patrols on its own, raises the alarm on its own, and stands down on its own. In this lesson, you learned:

* How a general object-detection model catches whole people, not just faces
* How a two-state system (patrolling / alarming) keeps the logic simple and reliable
* How Python decides and the sketch executes — clean cooperation across the two processors
* How a spoken alert is throttled so the guard warns without nagging
* How a timeout state returns the system to patrol after 3 quiet seconds

Your UNO Q can now watch a room like a security professional. The Edge AI module is complete — and every project in it began with the same question: *what does the camera see?* Your board has got very good at answering that. But it still cannot *understand* what it sees, answer a question about it, or act on a sentence you type. That is exactly where you are headed next.
