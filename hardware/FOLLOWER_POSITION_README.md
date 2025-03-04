# Follower Position Feedback System with Arm Identity

This feature adds real-time position reporting to the RoArm-M3 Pro follower arms, enabling data collection for imitation learning and real-time monitoring with automatic arm identification.

## Overview

When a RoArm-M3 Pro arm is configured in follower mode (ESP-NOW mode 3), it automatically reports its current joint positions and end-effector coordinates via the Serial (USB-C) port at 50Hz. Each arm includes its identity in the data stream, allowing the receiver to distinguish between different arms regardless of which USB port they are connected to. This data can be read by a connected computer (like the NVIDIA Jetson Orin Nano) for:

1. Training data collection for imitation learning
2. Real-time monitoring of arm positions
3. Validation of motion accuracy
4. Synchronization with other sensors (cameras, IMUs)

## Implementation

The implementation consists of:

1. `follower_position_feedback.h` - ESP32 header file with position reporting and arm identity
2. `RoArm-M3_example_with_feedback.ino` - Modified firmware with position reporting enabled
3. `uart_ctrl_with_identity.h` - Handler for arm identity commands
4. `read_follower_positions.py` - Python script to read and save the position data

## Arm Identity

Each follower arm can be assigned an identity that is:
- Stored in flash memory (survives power cycles)
- Included in every position data packet
- Used to identify the arm regardless of USB port assignment

To set the arm identity, send this JSON command:

```json
{"T":400,"arm_id":"follower_left"}
```

or for the right arm:

```json
{"T":400,"arm_id":"follower_right"}
```

## Data Format

The position data is output as JSON with the following format:

```json
{
  "arm_id": "follower_left", // Arm identity (follower_left or follower_right)
  "t": 12345,       // Timestamp (milliseconds since ESP32 startup)
  "b": 0.123,       // Base joint angle (radians)
  "s": 0.456,       // Shoulder joint angle (radians)
  "e": 0.789,       // Elbow joint angle (radians)
  "t": 0.012,       // Wrist tilt angle (radians)
  "r": 0.345,       // Wrist roll angle (radians)
  "g": 0.678,       // Gripper position (radians)
  "x": 100.0,       // End-effector X position (mm)
  "y": 150.0,       // End-effector Y position (mm)
  "z": 200.0,       // End-effector Z position (mm)
  "tilt": 0.1       // End-effector tilt (radians)
}
```

## Installation and Setup

### Flashing the Firmware

1. Connect to your RoArm-M3 Pro arm via USB
2. Flash the modified firmware using the Arduino IDE or PlatformIO
3. Verify the arm starts normally

### Setting Arm Identity

1. Connect to your RoArm-M3 Pro arm via USB
2. Connect to the arm's WiFi hotspot (SSID: RoArm-M3, Password: 12345678)
3. Access the web control panel at 192.168.4.1
4. Set the arm identity using the command:
   ```json
   {"T":400,"arm_id":"follower_left"}
   ```
   (or "follower_right" for the right arm)
5. Verify the identity appears on the OLED display

### Reading Position Data

1. Connect both follower arms (left and right) to your Jetson Nano via USB
2. Configure both arms in follower mode:
   ```json
   {"T":301,"mode":3,"dev":0,"cmd":0,"megs":0}
   ```
3. Run the Python script to read position data:
   ```bash
   python3 read_follower_positions.py --port /dev/ttyUSB0 --output positions.jsonl
   ```

## Isaac SDK Integration

For Isaac SDK integration, use the auto-detection mechanism to find arms by their identity:

1. The Isaac SDK codelet searches all available serial ports for devices
2. Each device is tested by reading data and checking the "arm_id" field
3. Once identified, the codelet maintains the connection and processes data
4. This works even if USB port assignments change between reboots

## Integration with Mobile ALOHA

For Mobile ALOHA-style data collection, the position data should be synchronized with camera frames and other sensor data. This can be achieved by:

1. Using the host timestamp (`host_time` and `host_datetime` added by the Python reader)
2. Sampling all sensors (cameras, IMUs) at the same rate or interpolating to match timestamps
3. Storing the synchronized data in a format suitable for training models

## Requirements

- RoArm-M3 Pro arm with ESP32 controller
- USB connection to host computer
- Python 3.6+ with pyserial package (for testing)
- Host computer (NVIDIA Jetson Orin Nano or similar)

## Frequency Adjustment

The default position reporting frequency is 50Hz, which balances data quality with processing overhead. This can be adjusted by modifying the `POSITION_REPORT_FREQUENCY` constant in `follower_position_feedback.h` if a different rate is needed.

## Notes

- Position reporting only happens when the arm is in follower mode (ESP-NOW mode 3)
- The reported positions are the actual servo positions from encoder feedback, not the commanded positions
- This feature doesn't interfere with normal follower operation
- The Serial port is shared with command input, so avoid sending commands while collecting position data
- Arm identity is displayed on the OLED screen for easy identification