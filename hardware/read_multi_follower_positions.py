#!/usr/bin/env python3
"""
Multi-Follower Position Reader

This script automatically detects and reads position data from multiple RoArm-M3 Pro 
follower arms, distinguishing them by their arm_id. It can handle both follower_left
and follower_right arms connected to the same computer.

Usage:
  python3 read_multi_follower_positions.py [--output folder_path]
"""

import argparse
import json
import os
import serial
import serial.tools.list_ports
import sys
import threading
import time
from datetime import datetime


def detect_arm(port, timeout=2.0):
    """
    Detect if the specified port has a RoArm-M3 follower arm and identify it.
    
    Args:
        port: Serial port to check
        timeout: Time limit for detection in seconds
        
    Returns:
        Arm identity string or None if not detected
    """
    try:
        # Open serial port
        ser = serial.Serial(port, 115200, timeout=0.1)
        
        # Set start time for timeout
        start_time = time.time()
        
        # Try to read data until timeout
        while time.time() - start_time < timeout:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    time.sleep(0.01)  # Short sleep to avoid busy waiting
                    continue
                    
                # Try to parse as JSON
                data = json.loads(line)
                
                # Check if it has arm_id field
                if 'arm_id' in data:
                    arm_id = data['arm_id']
                    ser.close()
                    return arm_id
                    
            except json.JSONDecodeError:
                # Not valid JSON, continue
                pass
            except UnicodeDecodeError:
                # Not valid UTF-8, continue
                pass
            
        # Close port if no arm detected
        ser.close()
        return None
        
    except serial.SerialException:
        # Port couldn't be opened or is not available
        return None


def find_follower_arms():
    """
    Scan all available serial ports and find all connected follower arms.
    
    Returns:
        Dictionary mapping arm IDs to port names
    """
    print("Scanning for follower arms...")
    
    # Get list of available ports
    ports = [p.device for p in serial.tools.list_ports.comports()]
    print(f"Found {len(ports)} serial ports: {', '.join(ports)}")
    
    # Check each port for RoArm-M3 follower arms
    arm_ports = {}
    for port in ports:
        print(f"Checking {port}...", end='', flush=True)
        arm_id = detect_arm(port)
        if arm_id:
            print(f" Found {arm_id}!")
            arm_ports[arm_id] = port
        else:
            print(" No arm detected")
    
    return arm_ports


def read_arm_data(arm_id, port, output_folder=None, stop_event=None):
    """
    Read position data from a specific arm continuously.
    
    Args:
        arm_id: Arm identifier string
        port: Serial port connected to this arm
        output_folder: Optional folder to save data files
        stop_event: Threading event to signal when to stop
    """
    print(f"Starting reader for {arm_id} on {port}")
    
    # Open output file if folder specified
    out_file = None
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{arm_id}_{timestamp}.jsonl"
        filepath = os.path.join(output_folder, filename)
        out_file = open(filepath, 'w')
        print(f"Saving {arm_id} data to {filepath}")
    
    try:
        # Open serial port
        ser = serial.Serial(port, 115200, timeout=1)
        
        # Read data until stopped
        while not (stop_event and stop_event.is_set()):
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                
                # Parse JSON data
                data = json.loads(line)
                
                # Validate that this is the correct arm
                if 'arm_id' not in data or data['arm_id'] != arm_id:
                    continue
                
                # Add host timestamp
                data['host_time'] = time.time()
                data['host_datetime'] = datetime.now().isoformat()
                
                # Display data
                print(f"[{arm_id}] t:{data['t']} b:{data['b']:.2f} s:{data['s']:.2f} e:{data['e']:.2f} x:{data['x']:.1f} y:{data['y']:.1f} z:{data['z']:.1f}")
                
                # Save data if output file specified
                if out_file:
                    out_file.write(json.dumps(data) + '\n')
                    out_file.flush()
                
            except json.JSONDecodeError:
                # Not valid JSON, continue
                pass
            except UnicodeDecodeError:
                # Not valid UTF-8, continue
                pass
            except Exception as e:
                print(f"Error reading from {arm_id}: {e}")
                time.sleep(0.1)  # Brief pause on error
    
    except KeyboardInterrupt:
        # Handle CTRL+C 
        pass
    finally:
        # Clean up
        if out_file:
            out_file.close()
        if 'ser' in locals() and ser.is_open:
            ser.close()
        
        print(f"Stopped reader for {arm_id}")


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Read and save position data from multiple RoArm-M3 Pro follower arms")
    parser.add_argument("--output", help="Output folder to save position data (JSONL format)")
    parser.add_argument("--duration", type=float, help="Duration in seconds to read data")
    args = parser.parse_args()
    
    # Find all connected follower arms
    arm_ports = find_follower_arms()
    
    if not arm_ports:
        print("No follower arms detected. Make sure they are connected and in follower mode.")
        return
    
    print(f"Found {len(arm_ports)} follower arms:")
    for arm_id, port in arm_ports.items():
        print(f"  {arm_id} on {port}")
    
    # Create threads for reading from each arm
    stop_event = threading.Event()
    threads = []
    
    for arm_id, port in arm_ports.items():
        thread = threading.Thread(target=read_arm_data, args=(arm_id, port, args.output, stop_event))
        thread.daemon = True
        threads.append(thread)
        thread.start()
    
    try:
        # Set timeout if duration specified
        if args.duration:
            time.sleep(args.duration)
            stop_event.set()
        else:
            # Wait until user interrupts with Ctrl+C
            while True:
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nStopping all readers...")
        stop_event.set()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("All readers stopped.")


if __name__ == "__main__":
    main()