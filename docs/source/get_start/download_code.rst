.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Download the Code
===================

All of the code for this course lives in one GitHub repository: **sunfounder/unoq-ai-kit**. Every lesson is published there as a package that App Lab can import directly, and this page explains how to get one.

1. Download a Lesson Package
-----------------------------

The fastest way through the course is to follow the lessons in order: the *Run the App* section of every lesson starts with a download link for that lesson's package.

#. Open the releases page: `github.com/sunfounder/unoq-ai-kit/releases/latest <https://github.com/sunfounder/unoq-ai-kit/releases/latest>`_.

#. Download the package for the lesson you are working on — or download every package at once if you prefer to keep the whole course on your computer.

   .. note::

      GitHub rewrites spaces in the file names it publishes, so the package for ``01 Hello LED`` downloads as ``01.Hello.LED.zip``. The contents are identical, and the app inside keeps its name: ``01 Hello LED``.

2. What Is Inside a Package
-----------------------------

Every package is one complete App Lab project. Unzip it and you will find:

* ``01 Hello LED/`` — the app folder

  * ``app.yaml`` — App metadata (name, icon, bricks)
  * ``README.md`` — Project description and usage guide
  * ``sketch/``

    * ``sketch.ino`` — Hardware control on the microcontroller
    * ``sketch.yaml`` — Sketch configuration and libraries

  * ``python/``

    * ``main.py`` — Python logic on the Linux processor

  * ``assets/`` — Web UI files, images, and wiring diagrams

The speech lessons carry the bricks they need inside the package, which is why those downloads are around 100 MB; the rest are a few hundred kilobytes.

3. Import a Lesson into App Lab
---------------------------------

App Lab imports apps as ``.zip`` files. To run a lesson:

#. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer**, and select the package you downloaded.

   .. image:: /img/app_import_app.png
      :width: 600

#. Click the imported app to open it, then click **Run** (▶) to upload it to the UNO Q.

Every lesson in the course is imported the same way, so the workflow becomes familiar quickly.

4. Keeping the Code Up to Date
--------------------------------

Whenever the course is updated, a new release appears on the same releases page. The download link in every lesson always points at the newest release, so downloading a package again gets you the latest version. Your own App Lab projects are stored inside App Lab and are not affected.

5. Browsing the Source
------------------------

If you would rather read the code without running it, or build your own packages, the whole repository is available at `github.com/sunfounder/unoq-ai-kit <https://github.com/sunfounder/unoq-ai-kit>`_ — each module folder contains one folder per lesson.
