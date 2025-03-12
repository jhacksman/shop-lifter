# XIAO ESP32S3 Sense UVC Webcam

A USB Video Class (UVC) webcam implementation for the XIAO ESP32S3 Sense board. This Arduino sketch turns your XIAO ESP32S3 Sense board into a USB webcam that can be used with any computer without requiring custom drivers.

## Features

- Standard UVC device compatible with all operating systems
- No custom drivers required - works with any webcam software
- Compatible with the default OV2640 camera on the XIAO ESP32S3 Sense board
- Works with standalone OV2640 cameras
- Multiple resolution support (VGA 640x480, QVGA 320x240)
- MJPEG compression for efficient bandwidth usage
- Lightweight implementation optimized for ESP32S3 memory constraints

## Hardware Requirements

- Seeed Studio XIAO ESP32S3 Sense board with OV2640 camera
- USB cable for connection to computer
- PSRAM enabled (included on XIAO ESP32S3 Sense board)

## Software Requirements

- Arduino IDE
- ESP32 board support package (version 2.0.0 or later)
- ESP32 camera library

## Installation

1. Install the Arduino IDE
2. Add ESP32 board support to Arduino IDE
   - In Arduino IDE: File > Preferences > Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools > Board > Boards Manager > Search for "esp32" and install
3. Install the ESP32 camera library
   - Sketch > Include Library > Manage Libraries
   - Search for "esp32-camera" and install
4. Open the `xiao_esp32s3_uvc_webcam.ino` sketch
5. Configure board settings:
   - Board: "XIAO_ESP32S3"
   - USB Mode: "USB-OTG"
   - USB CDC On Boot: "Enabled"
   - Partition Scheme: "Huge APP (3MB No OTA/1MB SPIFFS)"
   - PSRAM: "QSPI PSRAM"
6. Upload the sketch to your XIAO ESP32S3 Sense board

## Usage

1. Connect the XIAO ESP32S3 Sense board to your computer via USB
2. The device will appear as a standard USB webcam
3. Use any webcam software (like Zoom, Teams, OBS, etc.) to view the camera feed

## Configuration

You can modify the following parameters in the sketch:

- `FRAME_SIZE`: Camera resolution (default: VGA 640x480)
- `JPEG_QUALITY`: JPEG compression quality (0-63, lower is better quality)
- `DEBUG_OUTPUT`: Enable/disable debug output via Serial
- `UVC_FPS`: Target frames per second (default: 15)
- `UVC_BUFFER_SIZE`: Size of the buffer for UVC frames (default: 32KB)

## How It Works

This implementation uses the ESP32S3's USB capabilities to create a standard UVC device:

1. The camera captures JPEG frames using the ESP32 camera library
2. The UVC task processes these frames and sends them over USB
3. USB descriptors define the device as a standard UVC webcam
4. The host computer recognizes the device as a standard webcam without needing drivers

## Troubleshooting

- If the camera fails to initialize, check the connections and power supply
- If the webcam is not recognized by your computer, try a different USB port or cable
- For more detailed debugging, enable `DEBUG_OUTPUT` in the sketch
- If you experience frame drops, try reducing the resolution or increasing the buffer size

## License

This project is licensed under the MIT License - see the LICENSE file for details.
