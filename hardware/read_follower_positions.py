#!/usr/bin/env python3
"""
Follower Position Reader

This script reads the position data sent by the RoArm-M3 Pro follower arm
and can save it to a file for later analysis or training.

Usage:
  python3 read_follower_positions.py [--port /dev/ttyUSB0] [--output positions.jsonl]
"""

import argparse
import json
import serial
import time
from datetime import datetime


def read_follower_positions(port, output_file=None, duration=None):
    """
    Read position data from the follower arm via the specified serial port.
    
    Args:
        port: Serial port device name
        output_file: Optional file to save position data
        duration: Optional duration in seconds to read data (None for indefinite)
    """
    # Open serial port
    ser = serial.Serial(port, 115200, timeout=1)
    print(f"Connected to {port}")
    
    # Open output file if specified
    out_file = None
    if output_file:
        out_file = open(output_file, 'w')
        print(f"Saving position data to {output_file}")
    
    # Set start time if duration specified
    start_time = time.time()
    
    try:
        print("Receiving position data (Ctrl+C to stop)...")
        print("Timestamp\tBase\tShoulder\tElbow\tWrist\tRoll\tGripper")
        
        # Read data in a loop
        while True:
            # Check duration if specified
            if duration and (time.time() - start_time > duration):
                print(f"Duration of {duration} seconds reached.")
                break
            
            # Read a line from the serial port
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                
                # Parse JSON data
                data = json.loads(line)
                
                # Add host timestamp
                data['host_time'] = time.time()
                data['host_datetime'] = datetime.now().isoformat()
                
                # Display data
                print(f"{data['t']}\t{data['b']:.2f}\t{data['s']:.2f}\t{data['e']:.2f}\t{data['t']:.2f}\t{data['r']:.2f}\t{data['g']:.2f}")
                
                # Save data if output file specified
                if out_file:
                    out_file.write(json.dumps(data) + '\n')
                    out_file.flush()
                
            except json.JSONDecodeError:
                print(f"Invalid JSON: {line}")
            except UnicodeDecodeError:
                print("Unicode decode error, skipping data")
            except Exception as e:
                print(f"Error: {e}")
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        # Clean up
        if out_file:
            out_file.close()
        ser.close()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Read and save position data from RoArm-M3 Pro follower arm")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port device")
    parser.add_argument("--output", help="Output file to save position data (JSONL format)")
    parser.add_argument("--duration", type=float, help="Duration in seconds to read data")
    args = parser.parse_args()
    
    # Read positions
    read_follower_positions(args.port, args.output, args.duration)