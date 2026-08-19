.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Run Your First App
========================

**Overview**

In this section, you will learn how to run your first application in Arduino App Lab using the classic **Blink LED** example.  
You will also learn how to copy, edit, create, export, import applications, and optionally set an app to run automatically at startup.

--------------------------------------------------

Run Your First Example
------------------------------------

Running code traditionally starts with the **Blink LED** example.

#. Click the **Blink LED** app.

   .. image:: img/app_blink_led.png
      :width: 600

#. The application is organized as a project folder containing multiple subdirectories.

   A typical app structure includes three main files located in different folders:

   * ``main.py`` – The main entry point running on the Linux processor, written in Python®.  
   * ``sketch.ino`` – Contains all microcontroller code, written in Arduino (C/C++).  
   * ``app.yaml`` – Stores application metadata such as name, description, and used Bricks (not editable).  
   * Additional files may include ``README.md`` for documentation and other resources specific to the example.

   .. image:: img/app_open_blink.png
      :width: 600

#. Click the **Run** button in the top-right corner and wait for the application to load.

   .. image:: img/app_blink_run.png
      :width: 600

#. After running successfully, the **LED 3** on the UNO Q will blink red.

   .. image:: img/unoq_led3.png
      :width: 600

--------------------------------------------------

App Management (Create, Copy, Import & Export)
----------------------------------------------------------

**Run at Startup**

You can set an app to run automatically when the UNO Q powers on.  
This allows the device to start your application without manual interaction.

   .. image:: img/app_run_start.png

--------------------------------------------------

**Copy and Edit**

#. If you want to modify an app from **Examples**, you cannot edit it directly. Click the **Copy and edit app** button in the top-right corner.

   .. image:: img/app_blink_copy.png
      :width: 600

#. Customize the app name and icon based on your project, then click **Create New**.

   .. image:: img/app_copy_name.png
      :width: 600

#. The new app will appear under **Apps**.

   .. image:: img/app_my_apps.png
      :width: 600

--------------------------------------------------

**Create a New App**

#. You can also create a new app from scratch in the **Apps** page.

   .. image:: img/app_create_new.png
      :width: 600

#. Choose an icon and name for your app, then click **Create New**.

   .. image:: img/app_new_name.png
      :width: 600

#. The newly created app will appear under **Apps**.

   .. image:: img/app_new_app.png
      :width: 600

--------------------------------------------------

**Export App**

#. To share your app, click the **Export** button.

   .. image:: img/app_export.png
      :width: 600

#. You can export your app as a ``.zip`` package, which includes the app code, assets, configuration, and dependencies.

   .. image:: img/app_export_zip.png
      :width: 600

#. The exported file will be saved to your ``Downloads/`` folder by default.

   .. image:: img/app_export_save.png
      :width: 600

--------------------------------------------------

**Import App**

You can import apps created by yourself or shared by others.

#. In the **Apps** page, open the dropdown next to **Create new app +** and select **Import App**.

   .. image:: img/app_import.png
      :width: 600

#. Drag and drop your file or select **Import from computer**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select a ``.zip`` file and click **Open**.

   .. image:: img/app_import_open.png
      :width: 600

#. The imported app will appear under **Apps**.

   .. image:: img/app_import_in.png
      :width: 600

--------------------------------------------------

Summary
-------------------------------

You have now learned the basic operations in Arduino App Lab, including:

- Running an example app  
- Understanding app structure  
- Copying and editing apps  
- Creating new apps  
- Exporting and importing apps  
- Setting apps to run at startup  

Next, you will explore the differences between **Arduino App Lab** and the traditional **Arduino IDE**.