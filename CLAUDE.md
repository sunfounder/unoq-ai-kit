  # UNO Q AI Starter Kit — Project Documentation

## Project Overview

This is the documentation and course repository for the **SunFounder AI Starter Kit with Arduino Uno Q** (UNO Q AIoT Learning Kit). The kit targets beginners aged 10+, students, educators, and makers. Through hardware experiments, IoT applications, and AI technology practices, learners progress from basic hardware control to IoT systems to AI-powered devices.

- **GitHub**: sunfounder/unoq-ai-kit
- **Docs engine**: Sphinx (RST format, sphinx_rtd_theme)
- **Source**: `docs/source/`
- **Audience**: Beginners with zero programming or electronics experience
- **Language**: English

## Hardware Platform

- **Board**: Arduino UNO Q (Qualcomm QRB2210 MPU + STM32U585 MCU, dual-processor)
- **Expansion**: Robot Shield (battery management, motor/servo drivers, multi-rail power, onboard MCU)
- **Multimedia**: Multimedia Carrier (dual CSI cameras, DSI display, microphone, speaker, headphone jack, RGB LEDs, 10-axis IMU)
- **Sensors**: Ultrasonic, DHT11, photoresistor, thermistor, PIR motion sensor
- **Actuators**: Servos (×2, metal gear), DC motor + fan, active/passive buzzers, RGB LED, LEDs
- **Input**: Joystick, potentiometer, tilt switch, buttons
- **Components**: Breadboard, resistors (10Ω–1MΩ), transistors (NPN/PNP), capacitors, jumper wires

## Hardware Pin Assignments

The authoritative pin table for all lessons (updated 2026-09 for the new
RobotShield layout). Components may share pins because each lesson uses
only a subset:

| Component | Pin |
|-----------|-----|
| LED | D5 |
| 4-LED group | D4, D5, D6, D7 |
| Active / passive buzzer | D5 |
| Push button | D4 |
| Tilt switch | D4 |
| Photoresistor | A0 |
| PIR OUT | D4 |
| RGB LED | R→D8, G→D7, B→D6 |
| Motor (IN1/IN2) | D2, D3 |
| Pan servo | D9 |
| Tilt servo | D10 |
| Potentiometer | A2 |
| Ultrasonic | TRIG→D11, ECHO→D12 |
| DHT11 DATA | D4 |
| Thermistor | A1 |
| Joystick | SW→D4, X→A3, Y→A2 |
| Two buttons (game) | left→D7, right→D6 |

## Software Platform

- **Arduino App Lab**: Web-based IDE — the primary development tool for this course. No driver installation needed. Students create/edit/import/run apps in a browser-like environment.
- **Arduino IDE**: Introduced in a comparison lesson (Module A, lesson 13).
- **Edge Impulse**: Used in Module D for AI model training and deployment.
- **LLM Integration**: Module E connects to Gemini/ChatGPT for AI-driven hardware interaction.

## Course Structure (6 Modules)

| Module | Lessons | Theme |
|--------|---------|-------|
| A: Basic Interaction | 17 | Sketch-only hardware control — no Python, no Web UI |
| B: Multimedia | 9 | Camera, STT, TTS — no breadboard, Carrier-only |
| C: IoT | 9 | Bridge, Web UI, Python+Sketch hybrid |
| D: Edge AI | 9 | Camera + microphone, AI vision and voice, then physical response |
| E: AI & LLM | 7 | CloudLLM, natural language, Tool Calling |
| F: AI Projects | 4 | Vision + Voice + LLM fusion |

### Module A Lesson Order

1. Hello LED — digital output
2. Button-Controlled Light — digital input
3. Tilt Alarm — digital input + active buzzer
4. Photoresistor Night Light — analogRead (first analog lesson)
5. PIR Motion Alarm — digital sensor (motion) + active buzzer alarm
6. Color Mixer — RGB PWM color mixing
7. Motor Speed Controller — DC motor PWM
8. Servo Sweep — Arduino_HardwareServo library
9. Variable Pitch Melody — analog input + PWM audio
10. Ultrasonic Radar — timing-based sensor
11. Temperature & Humidity Monitor — DHT11 sensor
12. Thermistor-Controlled Fan — analog input + PWM motor
13. Joystick Servo — dual-axis control + auto-calibration
14. IMU Attitude — I2C + calibration (depends on 14 IMU Calibration)
15. IMU Servo — motion-controlled servo
16. LED Matrix Patterns — built-in 8×13 display
17. Opposite Reaction Game — game logic, button+buzzer+display

**Pedagogical principle**: Each lesson introduces at most one genuinely new concept. Everything else builds on previously learned knowledge, so students feel "I already know this, just one small new thing."

## Module Templates — Per-Module Canonical References

Each module has its own lesson template. These templates are NOT
interchangeable — when writing a lesson for a module, follow that
module's canonical reference exactly.

---

### Setup Section (all modules)

The first numbered section of every lesson is the Setup section
(**"1. Setup"** in basic, media, and edge AI; the iot module still uses
the old **"Build the Circuit"** title — convert when convenient). Its
structure is shared across all modules:

```
1. Setup / Build the Circuit
    - What You Need / Components Needed: list-table
      * :widths: 25 25 25 25 (4-col) or 25 25 (2-col), :header-rows: 0
      * Row 1: quantity + name — Pan Tilt Kit plain, components as :ref:
        links (e.g. `1 * :ref:`cpn_button``, `3 * :ref:`cpn_resistor` (220Ω)`)
      * Row 2: |list_xxx| image substitutions (|list_pan_tilt|,
        |list_button|, |list_220ohm|, ...)
      * Empty cells use `-`
      * NO .. note:: / .. tip:: / .. warning:: after the table — too many
        callouts clutter the page; fold the facts (resistor required, LED
        orientation, pull-up, built-in parts, servo power) into the Wiring
        Diagram sentence instead
        (exceptions: STT ZIP ~100 MB note, TTS first-run note — both live
        in the Run/Code section anyway)
    - Software Requirements (projects with Bricks/libraries): nested list
      * Bricks: what app.yaml declares (sunfounder_stt, sunfounder_tts, ...)
      * Libraries: ONLY real sketch.yaml libraries (Arduino_HardwareServo,
        DHT sensor library, ...) — bricks are NOT libraries
      * sketch.yaml libraries MUST include a version, e.g.
        ``- Arduino_HardwareServo (0.0.1)`` — without a version App Lab
        errors out
      * Projects with no bricks state so in prose (e.g. "the camera is an
        App Lab peripheral")
    - Wiring Diagram (breadboard lessons):
      * ONE concrete sentence describing the connections (pin names,
        resistor placement, orientation), folding in the safety-critical
        facts from any deleted tip/warning
      * .. image:: /img/wiring/wiring_*.png (absolute path)
      * If the image doesn't exist yet, keep the reference as a placeholder
    - One-time board setup steps (e.g. enabling external carriers for the
      camera) do NOT go in the lesson — they live in faq.rst with a
      `.. _anchor:` and lessons link to them with :ref:. Only a one-line
      pointer + :ref: link appears in the lesson.
```

---

### Module A: Basic Interaction (basic/)

**Canonical reference:** `basic/1_hello_led.rst`

Simple Arduino sketch lessons. Single `.ino` file with ``setup()`` /
``loop()``. Students wire components on a breadboard.

**Section checklist (follow `1_hello_led.rst` exactly):**

```
01 Lesson Title           <-- leading zero, capital first letters
======================

.. include:: /index.rst   <-- shared header, every lesson

Introduction
    - Hook sentence connecting to prior lessons
    - 3–5 learning objectives (bullet list)

1. Setup
    - What You Need: follows the shared Setup Section format (above)
    - Software Requirements (sketch-only projects):
      * With libraries: "This project uses the following sketch libraries:"
        + nested ``Libraries`` list matching sketch.yaml
      * Without libraries: "This project uses no external libraries — the
        sketch only uses the built-in Arduino framework."
    - NO .. tip:: / .. warning:: after the table — fold safety-critical
      facts (resistor required, LED orientation) into the Wiring Diagram
      sentence
    - Wiring Diagram: ONE concrete sentence with pin names + Fritzing
      breadboard image
    - NO Circuit Diagram — schematics were removed from all basic
      lessons (readers found them redundant with the Fritzing diagram)

2. Code
    - Import and Run the Code: #. auto-numbered steps with screenshots
      * For lessons using libraries: add .. note:: with :ref:`install_update_lib_c`
      * Do NOT include generic "Run button does nothing" troubleshooting
    - **The Sketch (sketch.ino)**: .. code-block:: cpp with :linenos: (shown AFTER running)
      Always use "The Sketch (sketch.ino)" as the heading — students need to
      know the exact file path.
    - How it Works:
        .. code-block:: text flow diagram (setup → loop rhythm)
        #. auto-numbered sections with code blocks + description bullets
        .. code-block:: arduino (NOT cpp inside How it Works)
        - description bullets before each code block

3. Experiment
    - Descriptive **bold sub-heading**
    - Guided table (input → effect)
    - **Challenge:** — with .. dropdown:: :open: solution

4. Troubleshooting
    - **bold heading** per issue (NOT a table)
    - * **Cause:** / * **Solution:** bullet format
    - 4–5 issues specific to the circuit — no generic items

5. Summary
    - Celebratory sentence + 3–5 bullet points
    - Tease next lesson
```

**Key RST patterns unique to Module A:**

- Flow diagram uses `.. code-block:: text` (NOT mermaid — that's for IoT).
- Full source code shown inline in `.. code-block:: cpp`.
- How it Works uses `#.` auto-numbered sections + `.. code-block:: arduino` + `-` description bullets. Each section groups 2–5 related lines with a paragraph of explanation.
- Code block header comment: description only, **no** lesson number or title. Use ``/*`` + one-line description + ``*/``.
- Experiment challenges use `.. dropdown::` with `:open:`.
- Shared import images: `app_import_app.png`, `app_import_pc.png`, `app_run.png`.

**How it Works format (since 2026-07-30):**

.. code-block:: text
   [flow diagram kept if present]

#. Section Title (no bold)

   - description bullet
   - description bullet

   .. code-block:: arduino

      [2–5 related lines of code]

#. Next Section Title

   - description bullet

   .. code-block:: arduino

      [next code group]

**Pan Tilt Kit:**

For lessons using the Robot Shield + servos + Multimedia Carrier + battery,
use the ``Pan Tilt Kit`` entry in Components Needed instead of listing each
item separately. The kit includes: UNO Q, Robot Shield, Multimedia Carrier,
2× servos, camera, battery, and structural parts — pre-assembled.

.. code-block:: rst

   * - 1 * Pan Tilt Kit
     - ...
   * - |list_pan_tilt|
     - ...

The ``|list_pan_tilt|`` substitution is defined in ``conf.py``.

**Library installation reminder:**

For lessons using Arduino_HardwareServo, SunFounder_IMU, or DHT sensor
library, add after the Run button step:

.. code-block:: rst

   .. note::

      This project uses the **Arduino_HardwareServo** library. see :ref:`install_update_lib_c`
      for installation or updating.

Servos on the UNO Q always use **Arduino_HardwareServo** (hardware PWM) —
the standard Servo library causes jitter on this board.

**Removed from all basic lessons:**
- Generic "Run button does nothing" troubleshooting — now in FAQ
- Long battery warnings — Robot Shield implicitly requires battery
- Functions described without parameters, e.g. write ``digitalWrite(ledPin, HIGH)`` not ``digitalWrite(HIGH)``

---

### Module B: Multimedia (media/)

**Canonical reference:** `media/3_local_stt.rst`

Python + Sketch App Lab projects using the Multimedia Carrier's speaker,
microphone, and camera. Follows the IoT lesson structure — the **Run the
App** section covers the run steps and How it Works only; full source code
is NOT shown (media projects have both ``main.py`` and ``sketch.ino``,
too long for the page).

**Section checklist (follow `3_local_stt.rst` exactly):**

```
03 Local STT               <-- leading zero in title, no zero in filename
===============

.. include:: /index.rst

Introduction
    - Hook sentence connecting to prior lessons
    - 3–5 learning objectives (bullet list)

1. Setup
    - Follows the shared Setup Section format (above), plus:
    - STT lessons: .. note:: the ZIP is ~100 MB (bundles the Whisper
      model) after Software Requirements

2. Run the App
    - NO "Import and Run the Code" sub-heading, NO "The Code" section
    - #. steps go directly under the section title
    - TTS lessons: .. note:: with the standard first-run text (below)
    - **How it Works** sub-heading:
        - .. code-block:: text flow for Python-only lessons (01, 03)
        - .. mermaid:: sequenceDiagram for lessons with sketch interaction
          (participants: Button/Sketch/Python)
        - Component explanations: **Sketch (sketch.ino)** / **Python (main.py)**
          with short snippets (5–10 lines) + description bullets

3. Experiment
    - Descriptive **bold sub-heading**
    - Guided table (input → expected result)
    - **Challenge:** — multi-step modification task, NO dropdown solution

4. Troubleshooting
    - **bold heading** per issue + * Cause: / * Solution: bullets
    - Focus: carrier attachment, STT/TTS first run, wiring, battery power
    - NO entries for bugs the shipped code already handles

5. Summary
    - Celebratory sentence + 3–5 bullet points
    - Tease next lesson
```

**Key rules unique to Module B:**

- No full source listings — only short How it Works snippets
- Servos always on **D9** (pan) / **D10** (tilt)
- Standard TTS first-run note (every TTS lesson): "The first time you run a
  TTS example on this UNO Q, App Lab needs to download and prepare the TTS
  runtime and audio dependencies. This may take half an hour or more ...
  This setup only happens once — after it finishes, every TTS example
  starts much faster."
- Filenames have no leading zero (``1_local_tts.rst``), titles do
  ("01 Local TTS")
- No ``docker-img-make`` or other internal build commands in
  Troubleshooting — students use App Lab, not the terminal
- Wiring images: ``/img/wiring/wiring_*.png``

---

### Module C: IoT (iot/)

**Canonical reference:** `iot/01_ui_led.rst`

Multi-file App Lab projects (Python + Sketch + HTML/JS/CSS + assets).
The **Code** section replaces inline source code with a project structure
breakdown and Mermaid sequence diagram. The **Build the Circuit** section
follows the shared Setup Section format (still titled "Build the Circuit"
with "Components Needed" in this module).

**Section checklist (follow `1_ui_led.rst` exactly):**

```
01 UI Control LED          <-- leading zero, title format
=====================

.. include:: /index.rst

Introduction
    - Hook sentence connecting to prior modules
    - 3–5 learning objectives (focus on architecture concepts)

1. Build the Circuit
    - Components Needed: SAME format as Module A (4-col, 2 sub-rows)
    - Wiring Diagram: Fritzing image. Brief text description OK here
      (circuit is usually simpler — same as a basic lesson).
      Text description goes ABOVE the image (same as Module A).
    - NO Circuit Diagram, NO .. warning:: (unless relevant)

2. Run the App
    - NO "Import and Run the Code" sub-heading — the #. steps go
      directly under the section title, fewer screenshots
      (only the result GIF at the end).
    - **How it Works** sub-heading: (NO inline source code — IoT
      projects are multi-file and too long for the page; describe the
      architecture instead)
        - Transition sentence
        - Project structure: RST nested list with Bricks / Libraries / Files
          * First lesson of module: list Bricks, Libraries, AND Files
          * Subsequent lessons: list only Files
        - .. mermaid:: sequenceDiagram (Browser → Python → Sketch → Hardware)
        - Component explanations: **Name (file)** — where it runs
          * API call — what it does (sub-bullets under each component)
    - Cloud lessons (05–06): section number shifts to 3 because a
      "2. Setup" section (Cloud account/Device/Thing/Dashboard) comes
      between Build the Circuit and Run the App. The Setup section
      covers only the Cloud-side setup (Device/Thing/Dashboard) —
      all import/run steps live under Run the App, same as every
      other lesson.

3. Experiment
    - Descriptive **bold sub-heading**
    - Guided table (CSS properties / code snippets → effect)
    - Code modification experiments (with .. code-block:: python)
    - **Challenge:** — multi-step integration task, NO dropdown solution

4. Troubleshooting
    - SAME format as Module A (**bold heading** + *Cause:*/*Solution:*)
    - Focus: Bridge errors, state sync, Web UI connectivity, file loading

5. Summary
    - SAME format as Module A
```

**Key differences from Module A:**

- **No inline source code** — show project structure as RST nested list instead.
- **Mermaid** `sequenceDiagram` for data flow (NOT `.. code-block:: text`).
- **No** `.. dropdown::` in Experiment (challenges are open-ended integration tasks).
- **No** Circuit Diagram, no `.. warning::` after wiring.
- Import steps are more compact (result GIF at end, not screenshot per step).
- Component explanations use bold headers with sub-bullets (see pattern below):

```rst
**Sketch (sketch.ino)** — runs on the STM32 MCU
  * Controls the hardware pin with ``digitalWrite()``
  * ``Bridge.provide()`` registers functions that Python can call
  * ``loop()`` is empty — everything is event-driven

**Python (main.py)** — runs on the Linux MPU
  * Hosts the ``WebUI`` server; browsers connect to it
  * ``ui.on_message()`` listens for events from the browser
  * ``Bridge.call()`` sends commands to the sketch
```

---

### Module D: Edge AI (edge_ai/)

**Canonical reference:** `edge_ai/01_ai_vision_recognition.rst`

AI/ML lessons using camera, microphone, and Edge Impulse models.
Minimal or no breadboard wiring — the hardware is the Multimedia Carrier
with its built-in peripherals.

**Section checklist (follow `01_ai_vision_recognition.rst` exactly):**

```
01 AI Vision Recognition   <-- two-digit number + space, same style as the iot module
============================

.. include:: /index.rst

Introduction
    - Hook sentence about AI capability
    - 3–5 learning objectives (focus on AI pipeline concepts)

1. Setup                   <-- "Setup", NOT "Build the Circuit"
    - What You Need: 4-col table (like Components Needed, but uses
      |list_xxx| placeholders, fewer :ref: links)
    - .. note:: for assembly reminders (NOT .. tip::)
    - Hardware Check: #. numbered physical setup steps
    - Hardware photo (camera/carrier, NOT Fritzing breadboard)

2. Run the App
    - ONE continuous #. list: the import steps (with
      /img/app_import_app.png and /img/app_import_pc.png), then the run
      steps (with /img/app_run.png and the result screenshot). NO
      "Import the Code" / "Run the Code" sub-headings.
    - TTS lessons: the first-run .. note:: sits inside this section
    - NO source code of any kind — no .. code-block:: python / cpp, no
      literalinclude. The reader already has the code in App Lab.
    - **How it Works**:
        - one short transition sentence
        - the project structure as an RST nested list (inline ``code``,
          never ASCII art), listing only the files that exist
        - one .. mermaid:: sequenceDiagram for the data path
          (participants + arrows only, no notes, never ASCII art)
        - then **Name (file)** — where it runs blocks whose bullets name
          the API calls (Sketch / Python / Bridge / Browser)

3. Experiment
    - Descriptive **bold sub-heading**
    - Guided table (objects → expected results)
    - **Challenge:** — open-ended, NO dropdown, NO code solution
      (observational: "test under different lighting")
    - **Challenge:** — another observational challenge

4. Troubleshooting
    - SAME format as Module A (**bold heading** + *Cause:*/*Solution:*)
    - Focus: camera connection, model loading, inference speed, lighting

5. Summary
    - SAME format as Module A
```

**Key differences from Module A and IoT:**

- Section 1 is **"Setup"** (not "Build the Circuit") — little or no
  breadboard work. The hardware is pre-assembled (camera + carrier), so the
  wiring sentence and image appear only in the lessons that add a component.
- **"What You Need"** table (not "Components Needed") — uses placeholder
  images for all items including the carrier and camera.
- **Software Requirements** lists the Bricks (and any real sketch libraries)
  the project declares.
- The result screenshot goes right after the introduction.
- **No source code anywhere.** The lessons show the project structure, a
  Mermaid data-path diagram, and per-file API bullets instead — exactly like
  the iot module.
- **Experiment** has NO dropdown solutions. Challenges are observational
  ("try different lighting", "test max distance").

## Writing Conventions

### Introduction
- One hook sentence. No concept primers (e.g., "What is an LED?").
- Component knowledge lives in separate `cpn_*.rst` files, referenced via
  `:ref:` links in the Components Needed table.

### Components Needed Table
- `.. list-table::` with `:widths: 25 25 25 25` and `:header-rows: 0`.
- Row 1: Quantity + `:ref:` links (e.g., `1 * :ref:\`Arduino Uno Q <cpn_uno_q>\``).
- Row 2: `|list_xxx|` image substitutions.
- Empty cells use `-`.

### Diagrams
- **Fritzing** (`*_fritzing.png`): Breadboard wiring. No accompanying text — the diagram is the single source of truth. Text descriptions easily fall out of sync when the diagram is updated.
- **Schematic** (`*_schematic.png`): REMOVED from basic lessons — no longer used.

### Directory Trees
- **Never** use ASCII art (``├──``, ``└──``, ``│``) in code blocks for directory structures — they misalign across fonts.
- Use **RST nested lists** instead. Each level is indented and prefixed with ``*``, with inline code for file/folder names:

  ```rst
  * ``1_ui_led/`` — the app folder
    * ``app.yaml`` — App metadata
    * ``python/``
      * ``main.py`` — Web server and Bridge communication
  ```

### Flow Diagrams
- **Never** use ASCII art for data flow, sequence, or architecture diagrams.
- Use **Mermaid** via the ``.. mermaid::`` directive (requires ``sphinxcontrib-mermaid`` in ``requirements.txt`` and ``conf.py``).
- Prefer ``sequenceDiagram`` for data flows (Browser → Python → Sketch → Hardware):

  ```rst
  .. mermaid::

     sequenceDiagram
         participant B as Browser (HTML/JS)
         participant P as Python (main.py)
         participant S as Sketch (sketch.ino)

         B->>P: socket.emit('toggle_led')
         P->>S: Bridge.call("set_led_state", True)
         S->>S: digitalWrite(5, HIGH)
         P-->>B: led_status_update
  ```

- Use ``flowchart`` for state machines or architecture overviews when needed.

### Code
- All code is delivered as `.zip` files for import into App Lab. The import workflow is identical across all lessons.
- Code blocks use `.. code-block:: cpp` with `:linenos:`.
- Show complete code once, after the student has run it and seen the result.

### Components
- Use `.. list-table::` with `|list_xxx|` image substitutions (defined in `conf.py`).
- 4 columns, no header row, 25/25/25/25 width ratio.
- Components that span rows (like Arduino) can appear alone in a row.

### No Lesson Number References

**Never** reference specific lesson numbers in RST lesson files or project
READMEs. The lesson order may change — numeric references would become stale
and require updating across every file.

Instead, use descriptive references:

- ❌ ``In Lesson 12, you used a joystick...``
- ✅ ``Earlier, you used a joystick...``
- ❌ ``the DHT11 from Lesson 10``
- ✅ ``the DHT11 you used earlier``
- ❌ ``the same pattern from Lesson 2``
- ✅ ``the same ``INPUT_PULLUP`` pattern you learned earlier``
- ❌ ``just like the LED pins in Lesson 4``
- ✅ ``just like the LED pin arrays you used earlier``

Acceptable alternatives (when referring to a specific future/other lesson
by topic, not number):

- ``the IMU calibration project``
- ``the previous lesson``
- ``the servo sweep lesson``
- ``the motor you used earlier``

### Lesson Numbering Convention

RST files and code folders use two numbering styles:

- **Lessons 1–4**: Old-style, no leading zero (``1_hello_led.rst``, ``2_button_led.rst``, ``3_tilt_alarm.rst``, ``4_photoresistor_led.rst``)
- **Lessons 5+**: New-style with leading zero (``05_pir_motion_alarm.rst``, ``06_color_mixer.rst``, etc.)

Code folders always use the two-digit format: ``01 Hello LED/``, ``05 PIR Motion Alarm/``.

When inserting a new lesson between existing ones, renumber all subsequent
lessons AND update every zip filename reference in RST files, READMEs, and
``app.yaml`` files. Use this checklist:

1. Rename code folders (highest → lowest to avoid conflicts)
2. Rename RST files
3. Update ``# NN`` title in every shifted README.md
4. Update ``name: NN`` in every shifted ``app.yaml``
5. Update ``Import `NN Name.zip``` in every shifted README
6. Update title number + underline in every shifted RST file
7. Update zip filename references in all RST ``:ref:`` and inline text
8. Update ``basic.rst`` toctree
9. Run a comprehensive grep for old numbers in all files

### README Step Numbering

In the **How to Use the Example** section, steps must be sequential with
no gaps. The base pattern is:

```
1. Open **Arduino App Lab**.
2. Select **My Apps** → ...
3. Download [`NN Name.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/NN.Name.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. [Expected result.]
```

For projects that require battery power, insert an additional step
between Import and Run:

```
3. Download [`NN Name.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/NN.Name.zip) and import it in **Arduino App Lab**.
4. Connect the battery pack to the Robot Shield.
5. Click **Run**.
6. [Expected result.]
```

For projects with extra setup steps (e.g. IMU calibration), add steps
after Run but before the result step. All numbering must be sequential.

### README Wiring Image Requirement

Every project that uses breadboard wiring **must** include a wiring image
in the Wiring section. The image file lives in ``assets/docs_assets/``
inside the project folder. The Wiring section format is:

```
## Wiring

[One short sentence describing the connection.]

![Wiring Diagram](assets/docs_assets/wiring_xxx.png)
```

Projects with no breadboard wiring (built-in LED matrix, IMU-only via QWIIC)
may explain this in text without an image.

> **Release download links.** The import step links straight to the lesson
> package on the releases page, using
> ``https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/<name>.zip``
> so the link keeps working when a new release is published. GitHub publishes
> asset names with dots instead of spaces (``NN Name.zip`` becomes
> ``NN.Name.zip``); the link text keeps the readable name. The *Run the App*
> step of the matching RST lesson uses the same URL in a ``:download:`` role.

### Zip Reference Consistency

The zip filename referenced in READMEs and RST files must match the
folder number:

- Folder ``05 PIR Motion Alarm/`` → ``05 PIR Motion Alarm.zip``
- Folder ``14 IMU Calibration/`` → ``14 IMU Calibration.zip``

When a lesson imports a **different** project's zip (e.g., IMU Servo
imports IMU Calibration), verify that the referenced zip matches the
**target** project's folder number, not the source lesson's number:

- ``15_imu_servo.rst`` → ``import ``14 IMU Calibration.zip``` ← correct (calibration project is at 14)

### Tone
- Conversational, encouraging, direct. Use "you" and "your".
- Explain why, not just what. Every component choice has a reason.
- Celebrate milestones ("You just built your first working circuit!").

### Images
- Placeholder naming: `<lesson_number>_<description>.png`
- Example: `1_hello_led_fritzing.png`, `1_hello_led_schematic.png`, `1_blink_result.gif`
- Images referenced as `img/filename.png` (Sphinx resolves from source dir).

### Wiring Diagrams Location

All wiring (Fritzing) diagrams live in one shared folder:
``docs/source/img/wiring/``, referenced with an **absolute path**:

.. code-block:: rst

   .. image:: /img/wiring/wiring_led.png

- Naming: ``wiring_<component>.png`` (e.g., ``wiring_pot_buzzer.png``,
  ``wiring_pc_buzzer_pir.png``)
- Lesson-specific screenshots (import dialogs, Serial Monitor, results)
  stay in each module's own ``img/`` folder (``basic/img/``, ``iot/img/``)
  and are referenced with the relative ``img/filename.png`` path.

### Shared App Screenshots Location

The three shared App Lab screenshots used by every lesson's import steps
live directly in ``docs/source/img/`` and are referenced with **absolute
paths**:

.. code-block:: rst

   .. image:: /img/app_import_app.png
   .. image:: /img/app_import_pc.png
   .. image:: /img/app_run.png

Never reference these with a relative ``img/`` path — the files exist only
at the ``img/`` root, not in each module's ``img/`` folder.

## File Organization

```
docs/source/
├── index.rst                    # Home page
├── conf.py                      # Sphinx config (substitutions, extensions)
├── 大纲.rst                     # Course outline (Chinese, authoritative)
├── faq.rst                      # FAQ
├── get_start/                   # Getting Started (before lessons)
│   ├── get_start.rst
│   ├── uno_q.rst
│   ├── robot_shield.rst
│   ├── app_lab.rst
│   ├── first_app.rst
│   └── arduino_ide.rst
├── basic/                       # Module A: Basic Interaction
│   ├── basic.rst                # Module index + toctree
│   └── <n>_<lesson_name>.rst    # Individual lessons (1–17)
├── media/                       # Module B: Multimedia (STT, TTS, Camera)
├── iot/                         # Module C: IoT
├── ai/                          # Module E: AI/LLM
├── edge_ai/                     # Module D: Edge AI
└── _static/                     # Static assets
    ├── img/
    ├── video/
    ├── pdf/
    └── zip/
```

## Code Delivery Convention

All lesson code is distributed as `.zip` files organized by module:

```
unoq-ai-kit/
├── basic/
│   ├── 1_hello_led.zip
│   ├── 2_button_led.zip
│   └── ...
├── iot/
├── ai/
└── edge_ai/
```

The student imports these via: App Lab → Import App → navigate to folder → select `.zip`.

## IoT Web UI Design System

This is the canonical design for all Module C (IoT) web UIs. The
`01 UI Control LED` project is the reference implementation. **Future
IoT UIs must follow this design system exactly — only change
functionality and text, never layout or colors.**

### Reference Files

```
iot/01 UI Control LED/assets/
├── index.html
├── style.css
└── app.js
```

### Color Palette

| Role | Color | Usage |
|------|-------|-------|
| Primary accent | `#29a3d9` | Title, status dot (connected), button ON state, glow effects — matches SunFounder logo |
| Title text | `#23425d` | Header `<h1>` text |
| Card background | `#fff` | `.card` container |
| Page background | `#eceff1` | `body` |
| Button OFF border | `#cfd8dc` | `#led-button.led-off` |
| Button OFF text | `#90a4ae` | Subtle gray |
| Status text | `#607d8b` | `#status-text` |
| Error | `#d32f2f` / `#ffebee` | Status dot + error banner |

### Layout Structure

```
┌─ header (white bg, bottom border) ─────────────────────┐
│ [logo left]          Title (centered, bold)             │
└─────────────────────────────────────────────────────────┘
┌─ main (centered) ───────────────────────────────────────┐
│  ┌─ .card (white, 12px radius, subtle shadow) ────────┐ │
│  │  .status-row   ● Ready / Connected / Disconnected   │ │
│  │                                                     │ │
│  │         ┌──────────────┐                            │ │
│  │         │  LED Button  │  ← 144px circle            │ │
│  │         │   LED IS OFF │     OFF: white + gray border│ │
│  │         └──────────────┘     ON: #29a3d9 fill + glow│ │
│  │                                                     │ │
│  │         Click to control the LED                    │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Key CSS Patterns

- **Header**: flexbox, logo `position: absolute; left: 40px`, title `flex: 1; text-align: center; font-weight: 700; font-size: 30px`
- **Card**: white bg, `border-radius: 12px`, multi-layer subtle `box-shadow`, `min-width: 360px; max-width: 420px`
- **LED Button**: `144px` circle, `border-radius: 50%`, `transition: 0.25s` on background/box-shadow/color. ON state fills entire circle with `#29a3d9` + outer glow ring
- **Status dot**: `8px` circle with `box-shadow` ring for connected/error states

### JS Initialization Pattern

Always call `setDefaultUI()` immediately on `DOMContentLoaded`, **before**
socket init. This ensures the HTML preview matches the running state:

```js
function setDefaultUI() {
    ledButton.className = 'led-off';
    ledButton.textContent = 'LED IS OFF';
    statusText.textContent = 'Click to control the LED';
    // ...
}

document.addEventListener('DOMContentLoaded', () => {
    setDefaultUI();   // ← first, no socket dependency
    initSocketIO();   // ← then connect for live updates
});
```

### Camera Preview Standard (all modules)

Every Web UI that shows the live camera feed uses the same frame size —
canonical reference: `iot/08 Smart Doorbell` and
`iot/09 IoT Security Monitor` (both identical). Edge AI lessons follow
the same standard.

```css
.camera-container {
    width: 100%;
    max-width: 640px;
    margin: 0 auto;
    aspect-ratio: 4 / 3;
    background: #1a1a2e;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}

.camera-stream {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border: 0;
    border-radius: 10px;
    background: #000;
}
```

Key facts: container max-width **640px** with **4:3** aspect ratio,
centered with `margin: 0 auto`, dark background (`#1a1a2e`), and the
frame uses `object-fit: contain` (never crops). The surrounding card is
`max-width: 820px`. Placeholder states (camera icon + "Starting
camera...") fill the same container.

### Rules for Future IoT UIs

1. **Same layout**: header (logo left, title center) + main card — do not restructure
2. **Same colors**: use `#29a3d9` for accent, `#23425d` for title, `#eceff1` background
3. **Same button style**: circle, border → solid fill on active state
4. **Same status row**: dot + label at top of card
5. **Only change**: button text, description text, JS socket events, and hardware-specific logic
6. **Zip packaging**: `app.yaml` must be at zip root — compress from inside the project folder, not the outer folder

---

### Code README Format (All Modules)

Every project folder must have a ``README.md``. This README sits alongside
the code in the same directory — it is imported into App Lab as part of the
project. Keep it concise: the code is right there, no need to duplicate it.

**Universal rules for ALL project READMEs (every module):**

1. **NO fenced code blocks anywhere** — `` ```arduino``, `` ```cpp``, `` ```python``, even `` ```text`` cause App Lab's README preview to freeze and become unscrollable. The markdown renderer's syntax highlighter is the culprit. Use inline `` `code` `` backticks, bold headings, and bullet lists instead. **This is the #1 rule — violates it and the preview breaks.**
2. **No `(install via Library Manager)`** — ``app.yaml`` / ``sketch.yaml`` declares libraries; App Lab auto-installs them.
3. **No troubleshooting section** — that belongs in the RST course docs, not in the project README.
4. **No Code Overview section** — the code lives in the same folder; README describes behavior, not implementation.
5. **Result image after the description** — every project README shows one result screenshot right after the one-sentence description: ``![Result](assets/docs_assets/<result_image>.png)``. The wiring image belongs only in the Wiring section.
6. **Wiring section** = one short sentence + one ``![Wiring Diagram](assets/docs_assets/wiring_xxx.png)`` image. No bullet lists, no tables, no warnings.
7. **Hardware** = ``Pan Tilt Kit ×1`` as the first item, followed by breadboard components. The kit contains UNO Q, Robot Shield, Multimedia Carrier, 2× servos, camera, and battery — all pre-assembled. Do NOT list kit components individually.
8. **How it Works** uses plain markdown only: ``**Flow**`` bullet list for setup/loop, then ``**Descriptive Title**`` subsections with 1–3 sentence explanations. Function names and values use inline `` `code` `` backticks.
9. **Software before Hardware** — if the project uses Bricks or Libraries, those sections come first.

---

### Module A: Basic Interaction (basic/)

**Canonical reference:** `basic/01 Hello LED/README.md`

Sketch-only projects. No web UI, no Python logic, no bricks.
Hardware is controlled entirely from ``sketch.ino``.

**README template:**

```
# NN Lesson Title

One-sentence description of what the project does.

![Result](assets/docs_assets/<result_image>.png)

## Libraries Used

- **LibraryName** library
(Only if the project uses external libraries — RobotShield, DHT, etc.)

## Hardware

- Pan Tilt Kit ×1
- Breadboard ×1
- Component ×1
- ...

## Wiring

[One short sentence describing the connection.]

![Wiring Diagram](assets/docs_assets/wiring_xxx.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [`NN Name.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/NN.Name.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. [Expected result.]

## How it Works

```text
setup() → runs once at startup:
    [brief steps]

loop() → runs over and over forever:
    [brief steps]
```

- Key concept explained in one bullet.
```

---

### Module B: Multimedia (media/)

**Canonical reference:** `media/01 Local TTS/README.md`

Pure Python lessons using the Multimedia Carrier's speaker, microphone,
and camera. No breadboard wiring — all hardware is built into the carrier.
Projects use bricks to access STT, TTS, and camera capabilities.

**README checklist (follow `01 Local TTS/README.md` exactly):**

```
# NN Lesson Title

One-sentence description of what the project does.

![Result](assets/docs_assets/<result_image>.png)

## Software

### Bricks Used

This example uses the following Bricks:

- `brick_name` — One-line description

### Libraries Used

- **LibraryName** library
(Only if sketch.yaml declares libraries — Arduino_HardwareServo, DHT sensor library, ...)

## Hardware

- Pan Tilt Kit ×1
- Component ×1
- ...

## Wiring

[Brief wiring description. "No breadboard wiring is needed" if built-in.]

![Wiring Diagram](assets/docs_assets/wiring_xxx.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [`NN Name.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/NN.Name.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. [Expected result.]

> **Note:** (TTS lessons only) The first time you run a TTS example on this
UNO Q, App Lab needs to download and prepare the TTS runtime and audio
dependencies. This may take half an hour or more, depending on your network
connection. Keep the UNO Q connected to the Internet and wait for the setup
to complete. This setup only happens once — after it finishes, every TTS
example starts much faster.

## How it Works

- step 1 → description
- step 2 → description

- Explanation bullet
- Explanation bullet
```

**Format rules:**
- **Software** (Bricks + Libraries) comes BEFORE Hardware — software defines what the project needs
- **Libraries Used** lists ONLY real sketch.yaml libraries — bricks are declared in app.yaml, they are NOT libraries
- Hardware is a simple bullet list (**Pan Tilt Kit ×1** first, kit components never listed individually)
- Wiring section = one short sentence + one image; the image may stay a placeholder while waiting for the PNG
- **No Code Overview section** — the code lives in the same folder; README describes behavior, not implementation
- **How it Works** uses a plain-markdown arrow flow (NO fenced blocks), then explanation bullets
- All fenced code blocks (```text / ```python / ```cpp) are forbidden — they freeze the App Lab README preview

**Key differences from Module A:**

- Section 1 is **"Wiring"** (not "Build the Circuit") — no breadboard, no resistor table. Just state that the hardware is built-in.
- **"Bricks Used"** section lists each brick declared in `app.yaml` with a one-line description.
- **"Libraries"** section lists installable libraries for the sketch side.
- **How it Works** uses a plain-markdown arrow flow, not code-block diagrams.
- Projects need both `app.yaml` with `python: entry: python/main.py` and `bricks:` declarations, plus a `sketch/` folder with minimal `sketch.ino` + `sketch.yaml`.

**Brick reference for Media module:**

| Brick | Description |
|-------|-------------|
| `robot_shield` | Access to Robot Shield hardware (I2C, GPIO, audio, PWM) |
| `sunfounder_stt` | Local speech-to-text (Whisper model) |
| `sunfounder_tts` | Local text-to-speech (EdgeTTS) |

**Library reference for Media module:**

| Library | Used by Brick |
|---------|--------------|
| RobotShield | `robot_shield` |
| SunFounder_STT | `sunfounder_stt` |
| SunFounder_TTS | `sunfounder_tts` |
