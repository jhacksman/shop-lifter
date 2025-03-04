"""
Implementation of leader-follower functionality for RoArm-M3 Pro.

This module provides classes for configuring and using the leader-follower mode
of the RoArm-M3 Pro robotic arms. It allows one arm to act as a leader and transmit
joint positions to follower arms, which then replicate the leader's movements.

Research references:
- Leader-Follower Mode: RoArm-M3/leader_follower_mode/README.md
- ESP-NOW Protocol: Communication protocol used for leader-follower functionality
"""

from typing import Dict, List, Union, Optional
from .arm_controller import ArmController


class LeaderController:
    """Controls a leader arm that broadcasts to followers."""
    
    def __init__(self, arm_controller: ArmController, mode: str = 'broadcast'):
        """
        Initialize leader controller.
        
        Args:
            arm_controller: ArmController instance
            mode: Either 'broadcast' (multiple followers) or 'single' (one follower)
        
        Raises:
            ValueError: If mode is invalid
        """
        self.arm = arm_controller
        
        if mode == 'broadcast':
            self.mode_value = 1  # F-LEADER-B (Flow-Leader Broadcast) mode
        elif mode == 'single':
            self.mode_value = 2  # F-LEADER-S (Flow-Leader Single) mode
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'broadcast' or 'single'")
            
        self.followers = []
        self.broadcasting = False
        
    def configure_as_leader(self) -> Dict:
        """
        Configure the arm as a leader.
        
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 301,  # CMD_ESP_NOW_CONFIG
            "mode": self.mode_value,
            "dev": 0,
            "cmd": 0,
            "megs": 0
        }
        return self.arm.send_command(cmd)
        
    def add_follower(self, mac_address: str) -> Dict:
        """
        Add a follower arm by MAC address.
        
        Args:
            mac_address: MAC address of the follower arm
            
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 303,  # CMD_ESP_NOW_ADD_FOLLOWER
            "mac": mac_address
        }
        response = self.arm.send_command(cmd)
        if response.get("status", "") == "ok":
            self.followers.append(mac_address)
        return response
        
    def remove_follower(self, mac_address: str) -> Dict:
        """
        Remove a follower arm.
        
        Args:
            mac_address: MAC address of the follower arm
            
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 304,  # CMD_ESP_NOW_REMOVE_FOLLOWER
            "mac": mac_address
        }
        response = self.arm.send_command(cmd)
        if response.get("status", "") == "ok" and mac_address in self.followers:
            self.followers.remove(mac_address)
        return response
        
    def start_broadcasting(self) -> Dict:
        """
        Start broadcasting movements to followers.
        
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 300,  # CMD_BROADCAST_FOLLOWER
            "mode": 1,
            "mac": "FF:FF:FF:FF:FF:FF"  # Broadcast address
        }
        response = self.arm.send_command(cmd)
        if response.get("status", "") == "ok":
            self.broadcasting = True
        return response
        
    def stop_broadcasting(self) -> Dict:
        """
        Stop broadcasting movements to followers.
        
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 300,  # CMD_BROADCAST_FOLLOWER
            "mode": 0,
            "mac": "FF:FF:FF:FF:FF:FF"  # Broadcast address
        }
        response = self.arm.send_command(cmd)
        if response.get("status", "") == "ok":
            self.broadcasting = False
        return response
        
    def control_all_followers(self, joint_positions: Dict[str, float]) -> Dict:
        """
        Send joint positions to all followers.
        
        Args:
            joint_positions: Dictionary of joint positions
                Keys: 'b' (base), 's' (shoulder), 'e' (elbow), 
                      't' (wrist), 'r' (roll), 'h' (hand)
                Values: Joint angles in radians
                
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 305,  # CMD_ESP_NOW_MANY_CTRL
            "dev": 0,
            "b": joint_positions.get("b", 0),
            "s": joint_positions.get("s", 0),
            "e": joint_positions.get("e", 0),
            "t": joint_positions.get("t", 0),
            "r": joint_positions.get("r", 0),
            "h": joint_positions.get("h", 0),
            "cmd": 0,
            "megs": "position update"
        }
        return self.arm.send_command(cmd)
    
    def control_specific_follower(self, mac_address: str, joint_positions: Dict[str, float]) -> Dict:
        """
        Send joint positions to a specific follower.
        
        Args:
            mac_address: MAC address of the follower arm
            joint_positions: Dictionary of joint positions
                Keys: 'b' (base), 's' (shoulder), 'e' (elbow), 
                      't' (wrist), 'r' (roll), 'h' (hand)
                Values: Joint angles in radians
                
        Returns:
            Response from the arm
        """
        cmd = {
            "T": 306,  # CMD_ESP_NOW_SINGLE
            "mac": mac_address,
            "dev": 0,
            "b": joint_positions.get("b", 0),
            "s": joint_positions.get("s", 0),
            "e": joint_positions.get("e", 0),
            "t": joint_positions.get("t", 0),
            "r": joint_positions.get("r", 0),
            "h": joint_positions.get("h", 0),
            "cmd": 0,
            "megs": "position update"
        }
        return self.arm.send_command(cmd)


class FollowerController:
    """Controls a follower arm that receives from a leader."""
    
    def __init__(self, arm_controller: ArmController):
        """
        Initialize follower controller.
        
        Args:
            arm_controller: ArmController instance
        """
        self.arm = arm_controller
        self.leader_mac = None
        
    def configure_as_follower(self, leader_mac: str) -> Dict:
        """
        Configure the arm as a follower.
        
        Args:
            leader_mac: MAC address of the leader arm
            
        Returns:
            Response from the arm
        """
        # First add the leader's MAC address
        add_cmd = {
            "T": 303,  # CMD_ESP_NOW_ADD_FOLLOWER (used for both leader and follower)
            "mac": leader_mac
        }
        add_response = self.arm.send_command(add_cmd)
        
        # Then set follower mode
        mode_cmd = {
            "T": 301,  # CMD_ESP_NOW_CONFIG
            "mode": 3,  # FOLLOWER mode
            "dev": 0,
            "cmd": 0,
            "megs": 0
        }
        mode_response = self.arm.send_command(mode_cmd)
        
        if mode_response.get("status", "") == "ok":
            self.leader_mac = leader_mac
            
        return mode_response
        
    def get_status(self) -> Dict:
        """
        Get current follower status.
        
        Returns:
            Status information
        """
        # There's no direct command for follower status
        # We can use the general ESP-NOW config query
        cmd = {
            "T": 301,  # CMD_ESP_NOW_CONFIG with no parameters acts as query
            "mode": -1  # Query mode
        }
        return self.arm.send_command(cmd)


# Example usage of Leader-Follower mode
if __name__ == "__main__":
    import time
    
    # Create controllers for two arms
    leader_arm = ArmController(connection_type='http', address='192.168.4.1')
    follower_arm = ArmController(connection_type='http', address='192.168.4.2')
    
    # Get MAC addresses
    leader_mac = leader_arm.get_mac_address()
    follower_mac = follower_arm.get_mac_address()
    print(f"Leader MAC: {leader_mac}")
    print(f"Follower MAC: {follower_mac}")
    
    # Initialize leader and follower controllers
    leader = LeaderController(leader_arm, mode='broadcast')
    follower = FollowerController(follower_arm)
    
    # Configure leader and follower
    print("Configuring leader...")
    leader.configure_as_leader()
    
    print("Adding follower to leader...")
    leader.add_follower(follower_mac)
    
    print("Configuring follower...")
    follower.configure_as_follower(leader_mac)
    
    # Start broadcasting
    print("Starting leader broadcast...")
    leader.start_broadcasting()
    
    # Now, any movement of the leader will be reflected in the follower
    # We can also directly control the followers
    print("Sending direct command to followers...")
    joint_positions = {
        "b": 0.0,  # Base
        "s": 0.5,  # Shoulder
        "e": 1.0,  # Elbow
        "t": 0.0,  # Wrist tilt
        "r": 0.0,  # Wrist roll
        "h": 0.8   # Hand (gripper)
    }
    leader.control_all_followers(joint_positions)
    
    # Wait for movement to complete
    time.sleep(3)
    
    # Stop broadcasting
    print("Stopping broadcast...")
    leader.stop_broadcasting()
    
    print("Leader-follower demo complete.")