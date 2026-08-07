.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

9. Train Your Own AI Model
==============================

Until now, you've used pre-trained models that someone else built. In this lesson, you'll become the AI engineer — **collecting your own data, training your own model, and deploying it** to the UNO Q. Using **Edge Impulse**, a cloud platform for edge AI development, you'll create a custom gesture or sound recognition model from scratch.

In this lesson, you will learn to:

* Collect training data (images or audio) for your custom AI model
* Upload data to Edge Impulse and label it
* Train a neural network and evaluate its accuracy
* Export the trained model as a ``.eim`` file and deploy it to the UNO Q

1. The Edge Impulse Workflow
-------------------------------

Edge Impulse is a complete platform for building edge AI models. The workflow has five stages:

.. code-block:: text

   1. COLLECT  → Gather your own data (images, audio, sensor readings)
   2. LABEL    → Tag each sample with the correct category
   3. TRAIN    → Edge Impulse trains a neural network on your data
   4. TEST     → Evaluate accuracy on data the model hasn't seen
   5. DEPLOY   → Export as .eim file, run on UNO Q

.. image:: img/9_edge_impulse_workflow.png
   :width: 700
   :align: center

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * Camera Module
     - 1 * USB Cable
   * - |list_uno_q|
     - |list_uno_q|
     - |list_uno_q|
     - |list_usb_cable|

.. note::

   You'll also need a free **Edge Impulse account** at `edgeimpulse.com <https://www.edgeimpulse.com>`_. The data collection and training happen in your browser — no software installation required.

2. Step-by-Step: Custom Gesture Model
----------------------------------------

We'll walk through creating a **custom gesture recognition model** that distinguishes between your own hand signs. You can adapt this workflow for voice commands, object recognition, or any classification task.

**Step 1: Collect Data**

#. Connect your UNO Q to your computer and open **Edge Impulse** in your browser.

#. Go to **Data Acquisition** → select your UNO Q as the data source → choose **Camera** as the sensor.

#. For each gesture you want to recognize, collect at least 30–50 samples:

   * Hold your hand in the gesture pose in front of the camera
   * Click **Start sampling** to capture a 1-second image burst
   * Repeat with slightly different angles, distances, and lighting

#. Aim for at least **3 gestures** plus a **background/noise** class (empty frame). Example: "thumbs_up", "open_palm", "fist", "background".

.. image:: img/9_data_collection.png
   :width: 700
   :align: center

.. tip::

   More data = better model. Aim for 50+ samples per class. Vary the conditions: different hand positions, lighting, backgrounds. A model trained on diverse data generalizes better.

**Step 2: Label Your Data**

#. After collection, each sample needs a **label** — the correct answer the model should learn.

#. In Edge Impulse, select samples and apply labels: "thumbs_up", "open_palm", "fist", "background".

#. Split your data: use **80% for training** and **20% for testing**. Edge Impulse does this automatically.

**Step 3: Train the Model**

#. Go to **Impulse Design** → **Create Impulse**. Configure the pipeline:

   * **Image processing block**: Resizes images to 96×96 pixels, converts to grayscale (faster training)
   * **Learning block**: Classification — the neural network that learns gesture categories

#. Go to **Image** → **Generate Features**. This processes all your images into feature vectors — numerical representations the neural network can learn from.

#. Go to **Classifier** → **Start Training**. The training process:

   * Feeds batches of labeled images through the neural network
   * Compares predictions to correct labels
   * Adjusts internal weights to reduce error
   * Repeats for many epochs (typically 30–100)

#. After training, review the **confusion matrix** — it shows which gestures the model confuses with each other. A good model has high numbers on the diagonal.

.. image:: img/9_training_result.png
   :width: 700
   :align: center

**Step 4: Test the Model**

#. Go to **Model Testing** → **Classify All**. Edge Impulse runs the trained model on your test set (the 20% of data it hasn't seen).

#. Aim for **>85% accuracy**. If it's lower:

   * Collect more training data (especially for confused classes)
   * Try different image processing settings (color vs. grayscale, larger image size)
   * Increase training epochs

**Step 5: Deploy to UNO Q**

#. Go to **Deployment** → select **Arduino UNO Q** as the target.

#. Click **Build** to download the ``.eim`` model file.

#. Place the ``.eim`` file in your App Lab project's assets folder, replacing the pre-trained model.

#. Update the code to use your new model:

.. code-block:: cpp

   AI.begin("my_custom_gestures.eim");  // Your trained model

.. image:: img/9_deployment.png
   :width: 600
   :align: center

3. Experiment
----------------

**Try a Different Modality**

Now that you know the workflow, apply it to a different type of data:

* **Audio**: Record voice commands ("start", "stop", "faster", "slower") using the onboard microphone. The pipeline is the same — just select **Microphone** as the sensor in data acquisition.
* **Sensor data**: Connect the DHT11 or an accelerometer and record time-series data (temperature patterns, motion gestures). Edge Impulse supports time-series classification for sensor-based AI.

**Challenge: Model Comparison**

Train two versions of the same model — one with 20 samples per class, one with 50 samples per class. Compare their test accuracy. How much does more data improve performance?

**Challenge: On-Device Validation**

After deploying your custom model, test it under real conditions — different rooms, different people, different times of day. Real-world performance often differs from lab testing. Keep notes on when the model succeeds and fails.

4. Troubleshooting
--------------------

**Model accuracy is below 70% on the test set**

* **Cause:** Too little training data, or data is too similar across classes.
* **Solution:** Collect at least 50 samples per class with varied conditions. Make sure each gesture is visually distinct from others. Add a "background" class to help the model learn what NOT to recognize.

**Training fails or produces an error in Edge Impulse**

* **Cause:** Images are too large, or the processing block configuration is wrong.
* **Solution:** Resize images to 96×96 or smaller. Use grayscale (1 channel) instead of RGB (3 channels) to reduce computation. Check that all samples have valid labels.

**Model works in Edge Impulse but not on UNO Q**

* **Cause:** The .eim file wasn't built for the correct target, or the model is too large for the device.
* **Solution:** In Deployment, make sure "Arduino UNO Q" is selected as the target. If the model exceeds the device's memory, reduce input image size or use a simpler model architecture (fewer layers).

**One gesture consistently confused with another**

* **Cause:** The two gestures look too similar from the camera's perspective.
* **Solution:** Make the gestures more distinct. Add more training samples for both classes, emphasizing their differences. Check the confusion matrix to quantify the problem — if two classes have >20% confusion, they need better separation.

5. Summary
-------------

You're now an AI model builder! In this lesson, you learned:

* The complete Edge Impulse workflow: collect → label → train → test → deploy
* How to collect diverse training data for better model accuracy
* How to interpret a confusion matrix and diagnose model weaknesses
* How to deploy a custom .eim model to the UNO Q

You can now build custom AI models for any classification task — gestures, voice commands, object recognition, or sensor patterns. In the final lesson, you'll combine everything into a capstone project: an AI-powered smart security camera.
