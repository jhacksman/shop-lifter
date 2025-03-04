# Follower Position Feedback System

This feature adds real-time position reporting to the RoArm-M3 Pro follower arms, enabling data collection for imitation learning and real-time monitoring.

## Overview

When a RoArm-M3 Pro arm is configured in follower mode (ESP-NOW mode 3), it automatically reports its current joint positions and end-effector coordinates via the Serial (USB-C) port at 50Hz. This data can be read by a connected computer (like the NVIDIA Jetson Orin Nano) for:

1. Training data collection for imitation learning
2. Real-time monitoring of arm positions
3. Validation of motion accuracy
4. Synchronization with other sensors (cameras, IMUs)

## Implementation

The implementation consists of:

1. `follower_position_feedback.h` - ESP32 header file that adds position reporting functionality
2. `RoArm-M3_example_with_feedback.ino` - Modified firmware with position reporting enabled
3. `read_follower_positions.py` - Python script to read and save the position data

## Data Format

The position data is output as JSON with the following format:

```json
{
  "t": 12345,       // Timestamp (milliseconds since ESP32 startup)
  "b": 0.123,       // Base joint angle (radians)
  "s": 0.456,       // Shoulder joint angle (radians)
  "e": 0.789,       // Elbow joint angle (radians)
  "t": 0.012,       // Wrist tilt angle (radians)
  "r": 0.345,       // Wrist roll angle (radians)
  "g": 0.678,       // Gripper position (radians)
  "x": 100.0,       // End-effector X position (mm)
  "y": 150.0,       // End-effector Y position (mm)
  "z": 200.0        // End-effector Z position (mm)
}
```

## Installation

### Flashing the Firmware

1. Connect to your RoArm-M3 Pro arm via USB
2. Flash the modified firmware using the Arduino IDE or PlatformIO
3. Verify the arm starts normally

### Reading Position Data

1. Connect to your RoArm-M3 Pro arm via USB
2. Configure the arm in follower mode
3. Run the Python script to read position data:

```bash
python3 read_follower_positions.py --port /dev/ttyUSB0 --output positions.jsonl
```

## Integration with Mobile ALOHA

For Mobile ALOHA-style data collection, the position data should be synchronized with camera frames and other sensor data. This can be achieved by:

1. Using the host timestamp (`host_time` and `host_datetime` added by the Python reader)
2. Sampling all sensors (cameras, IMUs) at the same rate or interpolating to match timestamps
3. Storing the synchronized data in a format suitable for training models

## Requirements

- RoArm-M3 Pro arm with ESP32 controller
- USB connection to host computer
- Python 3.6+ with pyserial package
- Host computer (NVIDIA Jetson Orin Nano or similar)

## Frequency Adjustment

The default position reporting frequency is 50Hz, which balances data quality with processing overhead. This can be adjusted by modifying the `POSITION_REPORT_FREQUENCY` constant in `follower_position_feedback.h` if a different rate is needed.

## Notes

- Position reporting only happens when the arm is in follower mode (ESP-NOW mode 3)
- The reported positions are the actual servo positions from encoder feedback, not the commanded positions
- This feature doesn't interfere with normal follower operation
- The Serial port is shared with command input, so avoid sending commands while collecting position data