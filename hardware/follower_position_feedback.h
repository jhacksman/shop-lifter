/**
 * Follower Position Feedback System for RoArm-M3 Pro
 * 
 * This module enables RoArm-M3 Pro follower arms to output their actual servo positions
 * via Serial (USB-C) when the arm is in follower mode. The data is serialized as JSON
 * with arm identity for easy processing by the NVIDIA Jetson Orin Nano.
 */

#ifndef FOLLOWER_POSITION_FEEDBACK_H
#define FOLLOWER_POSITION_FEEDBACK_H

#include <Preferences.h>

// Position data reporting frequency (Hz)
#define POSITION_REPORT_FREQUENCY 50

// Default identity if not configured
String armIdentity = "unknown";

// Timestamp for position reporting
unsigned long lastPositionReportTime = 0;

/**
 * Set arm identity and store in flash memory
 * 
 * @param identity The identity string ("follower_left" or "follower_right")
 */
void setArmIdentity(String identity) {
  // Store identity in non-volatile memory
  Preferences preferences;
  preferences.begin("arm_config", false);
  preferences.putString("arm_id", identity);
  preferences.end();
  
  // Update current identity
  armIdentity = identity;
  
  // Update OLED display
  screenLine_3 = "Arm ID: " + identity;
  oled_update();
  
  // Log identity change
  if (InfoPrint == 1) {
    Serial.println("Arm identity set to: " + identity);
  }
}

/**
 * Get arm identity from flash memory
 * 
 * @return The stored identity string, or "unknown" if not set
 */
String getArmIdentity() {
  // Read identity from non-volatile memory
  Preferences preferences;
  preferences.begin("arm_config", true);
  String identity = preferences.getString("arm_id", "unknown");
  preferences.end();
  
  return identity;
}

/**
 * Initialize arm identity
 * 
 * This should be called during setup to load the stored identity
 */
void initArmIdentity() {
  // Load identity from flash
  armIdentity = getArmIdentity();
  
  // Show on OLED
  screenLine_3 = "Arm ID: " + armIdentity;
  oled_update();
  
  if (InfoPrint == 1) {
    Serial.println("Arm identity: " + armIdentity);
  }
}

/**
 * Send position data via serial
 * 
 * This function reads the actual servo positions and outputs them
 * in JSON format to the Serial (USB-C) port, including arm identity
 */
void sendPositionData() {
  // Get current servo positions from feedback
  // The RoArmM3_getPosByServoFeedback() is already called in the main loop
  
  // Create JSON document
  StaticJsonDocument<256> posData;
  
  // Add arm identifier
  posData["arm_id"] = armIdentity;
  
  // Add timestamp (milliseconds since startup)
  posData["t"] = millis();
  
  // Add joint angles (radians)
  posData["b"] = radB;    // Base
  posData["s"] = radS;    // Shoulder
  posData["e"] = radE;    // Elbow
  posData["t"] = radT;    // Wrist tilt
  posData["r"] = radR;    // Wrist roll
  posData["g"] = radG;    // Gripper
  
  // Add computed end-effector position
  posData["x"] = lastX;
  posData["y"] = lastY;
  posData["z"] = lastZ;
  posData["tilt"] = lastT;  // Tilt angle
  
  // Serialize and send the data
  serializeJson(posData, Serial);
  Serial.println(); // Add newline for easier parsing
}

/**
 * Handle position reporting in the main loop
 * 
 * This function should be called in the main loop
 * to send position data at the defined frequency
 * when the arm is in follower mode.
 */
void handlePositionReporting() {
  // Only send data when in follower mode
  if (espNowMode != 3) {
    return;
  }
  
  // Check if it's time to send position data
  unsigned long currentTime = millis();
  if (currentTime - lastPositionReportTime >= (1000 / POSITION_REPORT_FREQUENCY)) {
    sendPositionData();
    lastPositionReportTime = currentTime;
  }
}

#endif // FOLLOWER_POSITION_FEEDBACK_H