# XIAO ESP32S3 Sense USB Webcam

A lightweight USB webcam implementation for the XIAO ESP32S3 Sense board. This Arduino sketch turns your XIAO ESP32S3 Sense board into a USB webcam that can be used with any computer.

## Features

- Compatible with the default OV2640 camera on the XIAO ESP32S3 Sense board
- Works with standalone OV2640 cameras
- Configurable resolution and JPEG quality
- Lightweight implementation optimized for ESP32S3 memory constraints

## Hardware Requirements

- Seeed Studio XIAO ESP32S3 Sense board with OV2640 camera
- USB cable for connection to computer

## Software Requirements

- Arduino IDE
- ESP32 board support package (version 2.0.0 or later)
- ESP32 camera library

## Installation

1. Install the Arduino IDE
2. Add ESP32 board support to Arduino IDE
3. Install the ESP32 camera library
4. Open the `xiao_esp32s3_webcam.ino` sketch
5. Select "XIAO_ESP32S3" from the Arduino IDE board menu
6. Upload the sketch to your XIAO ESP32S3 Sense board

## Usage

1. Connect the XIAO ESP32S3 Sense board to your computer via USB
2. The device will appear as a USB webcam
3. Use any webcam software to view the camera feed

## Configuration

You can modify the following parameters in the sketch:

- `FRAME_SIZE`: Camera resolution (default: VGA 640x480)
- `JPEG_QUALITY`: JPEG compression quality (0-63, lower is better quality)
- `DEBUG_OUTPUT`: Enable/disable debug output via Serial

## Troubleshooting

- If the camera fails to initialize, check the connections and power supply
- If the webcam is not recognized by your computer, try a different USB port or cable
- For more detailed debugging, enable `DEBUG_OUTPUT` in the sketch

## License

This project is licensed under the MIT License - see the LICENSE file for details.
