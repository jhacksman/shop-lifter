"""
Interface to the RoArm-M3 Pro arms using JSON commands.

This module provides a Python wrapper around the JSON command API for controlling
RoArm-M3 Pro robotic arms. It supports both HTTP and Serial communication.

Research references:
- RoArm-M3 JSON Command System documentation
- RoArm-M3 Python API documentation
"""

import json
import requests
import time
from typing import Dict, List, Union, Optional, Tuple


class ArmController:
    """Controls a single RoArm-M3 Pro arm via HTTP or Serial."""
    
    def __init__(self, connection_type: str = 'http', address: str = '192.168.4.1', port: Optional[str] = None):
        """
        Initialize connection to arm.
        
        Args:
            connection_type: Either 'http' or 'serial'
            address: IP address for HTTP or device path for serial
            port: Serial port (for serial connection only)
        
        Raises:
            ValueError: If connection_type is invalid
        """
        self.connection_type = connection_type.lower()
        self.address = address
        self.port = port
        
        if self.connection_type == 'http':
            self.base_url = f"http://{self.address}/js"
        elif self.connection_type == 'serial':
            # Serial connection will be implemented in the future
            # Requires pyserial library
            self.serial_conn = None
            raise NotImplementedError("Serial connection not yet implemented")
        else:
            raise ValueError(f"Invalid connection type: {connection_type}. Use 'http' or 'serial'")
    
    def send_command(self, command: Dict) -> Dict:
        """
        Send a JSON command to the arm.
        
        Args:
            command: Dictionary containing the JSON command
            
        Returns:
            Dictionary containing the response
            
        Raises:
            ConnectionError: If communication with the arm fails
        """
        try:
            if self.connection_type == 'http':
                url = f"{self.base_url}?json={json.dumps(command)}"
                response = requests.get(url, timeout=5)
                return json.loads(response.text)
            else:
                # Serial implementation will go here
                pass
        except Exception as e:
            raise ConnectionError(f"Failed to communicate with arm: {str(e)}")
    
    def get_mac_address(self) -> str:
        """
        Get the MAC address of the arm.
        
        Returns:
            MAC address as string
        """
        cmd = {"T": 302}  # CMD_GET_MAC_ADDRESS
        response = self.send_command(cmd)
        return response.get("mac", "")
    
    def move_joint(self, joint_id: int, angle: float, speed: float = 50.0) -> Dict:
        """
        Move a specific joint to the given angle.
        
        Args:
            joint_id: Joint ID (0-5)
                0: Base rotation
                1: Shoulder joint
                2: Elbow joint
                3: Wrist pitch
                4: Wrist roll
                5: Gripper
            angle: Target angle in radians
            speed: Movement speed (0-100)
            
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 101,  # CMD_SINGLE_JOINT_CTRL
            "joint": joint_id,
            "rad": angle,
            "spd": speed
        }
        return self.send_command(cmd)
    
    def move_to_position(self, x: float, y: float, z: float, 
                          roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0, 
                          speed: float = 50.0) -> Dict:
        """
        Move arm end effector to a specific position using inverse kinematics.
        
        Args:
            x, y, z: Target position coordinates (in meters)
            roll, pitch, yaw: Target orientation (in radians)
            speed: Movement speed (0-100)
            
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 201,  # CMD_COORDCTRL_POS
            "x": x,
            "y": y,
            "z": z,
            "rx": roll,
            "ry": pitch,
            "rz": yaw,
            "spd": speed
        }
        return self.send_command(cmd)
    
    def get_current_position(self) -> Dict:
        """
        Get current end effector position and orientation.
        
        Returns:
            Dictionary with position and orientation information
        """
        cmd = {"T": 203}  # CMD_COORDCTRL_GET_POS
        return self.send_command(cmd)
    
    def get_joint_angles(self) -> Dict:
        """
        Get current joint angles.
        
        Returns:
            Dictionary with joint angle information
        """
        cmd = {"T": 103}  # CMD_GET_JOINT_ANGLES
        return self.send_command(cmd)
    
    def set_gripper(self, position: float, speed: float = 50.0) -> Dict:
        """
        Set gripper position.
        
        Args:
            position: Gripper position (0.0 = closed, 1.0 = open)
            speed: Movement speed (0-100)
            
        Returns:
            Response from the arm
        """
        # Convert gripper position to angle (0.0-1.0 -> appropriate radian range)
        # For RoArm-M3, gripper typically has a range of about 0 to 1.57 radians
        angle = position * 1.57
        return self.move_joint(5, angle, speed)
    
    def home_position(self) -> Dict:
        """
        Move arm to home position.
        
        Returns:
            Response from the arm
        """
        cmd = {"T": 205}  # CMD_COORDCTRL_HOME
        return self.send_command(cmd)
    
    def emergency_stop(self) -> Dict:
        """
        Emergency stop - immediately stops all movement.
        
        Returns:
            Response from the arm
        """
        cmd = {"T": 104}  # CMD_STOP_MOVING
        return self.send_command(cmd)


# Example usage
if __name__ == "__main__":
    # Connect to arm via HTTP
    arm = ArmController(connection_type='http', address='192.168.4.1')
    
    # Get arm information
    mac_address = arm.get_mac_address()
    print(f"ARM MAC Address: {mac_address}")
    
    # Get current position
    position = arm.get_current_position()
    print(f"Current position: {position}")
    
    # Move to home position
    print("Moving to home position...")
    arm.home_position()
    time.sleep(3)
    
    # Move a joint
    print("Moving base joint...")
    arm.move_joint(0, 0.5, 30)  # Move base joint to 0.5 radians at 30% speed
    time.sleep(2)
    
    # Open and close gripper
    print("Opening gripper...")
    arm.set_gripper(1.0, 50)  # Open gripper fully
    time.sleep(1)
    print("Closing gripper...")
    arm.set_gripper(0.2, 50)  # Close gripper mostly
    time.sleep(1)
    
    # Move to a specific position
    print("Moving to position...")
    arm.move_to_position(0.1, 0.1, 0.1, 0, 0, 0, 40)
    time.sleep(3)
    
    print("Done!")