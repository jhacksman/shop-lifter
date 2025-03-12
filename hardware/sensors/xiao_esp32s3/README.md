# XIAO ESP32S3 Sense Camera Module

This module provides a lightweight implementation for controlling the OV2640 camera on the XIAO ESP32S3 Sense board.

## Features

- Support for the default camera that ships with the XIAO ESP32S3 Sense board
- Compatible with standalone OV2640 cameras
- Adjustable resolution and JPEG quality
- Simple API for capturing images
- Simulation mode for development without hardware

## Usage

```python
from hardware.sensors.xiao_esp32s3.camera_controller import XiaoESP32S3Camera, CameraResolution

# Create camera controller
camera = XiaoESP32S3Camera(resolution=CameraResolution.VGA)

# Get camera information
info = camera.get_camera_info()
print(f"Camera info: {info}")

# Capture an image
image_data = camera.capture_image()
if image_data is not None:
    # Process the image data
    print(f"Captured image: {len(image_data)} bytes")

# Change resolution
camera.set_resolution(CameraResolution.QVGA)

# Change quality
camera.set_quality(10)

# Close camera
camera.close()
```

## Hardware Requirements

- XIAO ESP32S3 Sense board with OV2640 camera
- PSRAM enabled for higher resolutions and JPEG quality

## Dependencies

- ESP32 camera library (esp32cam)
