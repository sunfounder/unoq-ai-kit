# 03 Camera Preview

This App Lab project displays the CSI camera feed in a simple SunFounder web page.

## Hardware

- Arduino UNO Q
- Multimedia Carrier with CSI camera
- USB-C cable

## Camera setup

1. Open App Lab settings.
2. Enable the external carrier.
3. Configure the camera port as `type1-2lanes`.
4. Reboot the board.

## Run the project

1. Import this ZIP file into Arduino App Lab.
2. Click **Run**.
3. Open the Web UI to view the live camera feed.

## Note

App Lab's `video_object_detection` Brick is included because it provides the video preview service at port `4912`. The project does not register detection callbacks or show face-detection results; it only displays the live video stream.
