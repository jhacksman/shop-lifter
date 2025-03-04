/**
 * UART Control with Arm Identity Support
 * 
 * This is a modified version of the original uart_ctrl.h that adds
 * support for the arm identity command (CMD_SET_ARM_IDENTITY).
 */

// Command handler for incoming JSON commands
void jsonCmdReceiveHandler() {
  int cmdType = jsonCmdReceive["T"].as<int>();
  switch(cmdType) {
    // ... existing commands remain the same ...
    
    // Set arm identity for follower position feedback
    // {"T":400,"arm_id":"follower_left"}
    case CMD_SET_ARM_IDENTITY:
      setArmIdentity(jsonCmdReceive["arm_id"].as<String>());
      jsonInfoHttp.clear();
      jsonInfoHttp["status"] = "ok";
      jsonInfoHttp["arm_id"] = armIdentity;
      break;
      
    // ... other commands remain the same ...
  }
}

// No changes to serialCtrl function