.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Download the Code
===================

All of the code for this course lives in one GitHub repository: **sunfounder/unoq-ai-kit**. This page shows you how to download the repository and explains what you'll find inside it.

1. Download the Repository
-----------------------------

#. Open the repository page at `github.com/sunfounder/unoq-ai-kit <https://github.com/sunfounder/unoq-ai-kit>`_.


#. Click the green **Code** button and select **Download ZIP**. Save the ZIP file to your computer and extract it. You'll get a folder named ``unoq-ai-kit-main``.

#. Alternatively, you can download the ZIP directly from:

   :download:`github.com/sunfounder/unoq-ai-kit/archive/refs/heads/main.zip <https://github.com/sunfounder/unoq-ai-kit/archive/refs/heads/main.zip>`

2. Folder Structure
---------------------

Inside ``unoq-ai-kit-main`` you'll find one folder per course module:

* ``basic/`` — Module A lessons (hardware control with sketches)
* ``media/`` — Module B lessons (speaker, microphone, and camera)
* ``iot/`` — Module C lessons (web UI and Arduino Cloud)
* ``edge_ai/`` — Module D lessons (AI vision)
* ``ai/`` — Module E lessons (large language models)

Each module folder contains one project folder per lesson, named like ``01 Hello LED``. Every lesson project follows the same structure:

* ``01 Hello LED/`` — the app folder

  * ``app.yaml`` — App metadata (name, icon, bricks)
  * ``README.md`` — Project description and usage guide
  * ``sketch/``

    * ``sketch.ino`` — Hardware control on the microcontroller
    * ``sketch.yaml`` — Sketch configuration and libraries

  * ``python/``

    * ``main.py`` — Python logic on the Linux processor

  * ``assets/`` — Web UI files, images, and wiring diagrams

3. Import a Lesson into App Lab
--------------------------------

App Lab imports apps as ``.zip`` files. To run a lesson:

#. Right-click the lesson folder (for example, ``01 Hello LED``) and compress it into a ZIP file.

   Make sure the ``app.yaml`` file sits at the **root** of the ZIP — compress from inside the module folder, not from outside.

   .. image:: img/compress_zip.png
      :width: 600
      :align: center

#. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer**, and select your ZIP file.

   .. image:: /img/app_import_app.png
      :width: 600

#. Click the imported app to open it, then click **Run** (▶) to upload it to the UNO Q.

Each lesson's *How to Use the Example* section repeats these steps, so you'll become familiar with the workflow quickly.

4. Keeping the Code Up to Date
--------------------------------

If the repository is updated after you download it, you can download the ZIP again the same way and replace the old folder. Your own App Lab projects are stored in App Lab itself and are not affected.
