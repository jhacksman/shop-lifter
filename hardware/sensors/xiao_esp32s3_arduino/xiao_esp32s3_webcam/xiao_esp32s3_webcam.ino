/**
 * XIAO ESP32S3 Sense USB Webcam
 * 
 * A lightweight USB webcam implementation for the XIAO ESP32S3 Sense board.
 * Compatible with the default OV2640 camera and standalone OV2640 cameras.
 * 
 * This sketch initializes the camera and implements a USB webcam interface
 * using the ESP32S3's USB capabilities.
 * 
 * Board settings:
 * - Board: "XIAO_ESP32S3"
 * - USB Mode: "USB-OTG"
 * - USB CDC On Boot: "Enabled"
 * - Partition Scheme: "Huge APP (3MB No OTA/1MB SPIFFS)"
 * - PSRAM: "QSPI PSRAM"
 */

#include "esp_camera.h"
#include "USB.h"
#include "USBCDC.h"
#include "esp_system.h"

// Camera model selection
#define CAMERA_MODEL_XIAO_ESP32S3
#include "camera_pins.h"

// USB configuration
USBCDC USBSerial;
#define USB_WEBCAM_INTERFACE 2
#define USB_WEBCAM_EP_DATA   3

// Camera configuration
#define FRAME_SIZE FRAMESIZE_VGA  // 640x480
#define JPEG_QUALITY 12           // 0-63 (lower is better quality)

// Frame buffer
camera_fb_t *fb = NULL;
bool frame_ready = false;

// Debug flag
#define DEBUG_OUTPUT 1

void setup() {
  // Initialize serial port
  Serial.begin(115200);
  while(!Serial && millis() < 3000);
  
  Serial.println("XIAO ESP32S3 USB Webcam");
  
  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAME_SIZE;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = JPEG_QUALITY;
  config.fb_count = 2;
  
  // Check for PSRAM
  if(psramFound()) {
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    // Limit the frame size when PSRAM is not available
    config.frame_size = FRAMESIZE_SVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }
  
  // Initialize the camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  
  Serial.println("Camera initialized");
  
  // Get sensor settings
  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    // Initial settings
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_special_effect(s, 0); // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
    s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
    s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
    s->set_aec2(s, 0);           // 0 = disable , 1 = enable
    s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
    s->set_bpc(s, 0);            // 0 = disable , 1 = enable
    s->set_wpc(s, 1);            // 0 = disable , 1 = enable
    s->set_raw_gma(s, 1);        // 0 = disable , 1 = enable
    s->set_lenc(s, 1);           // 0 = disable , 1 = enable
    s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
    s->set_vflip(s, 0);          // 0 = disable , 1 = enable
    s->set_dcw(s, 1);            // 0 = disable , 1 = enable
  }
  
  // Initialize USB
  USBSerial.begin();
  USB.begin();
  
  Serial.println("USB initialized");
  Serial.println("XIAO ESP32S3 USB Webcam ready");
}

void loop() {
  // Capture frame from camera
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    delay(1000);
    return;
  }
  
  // Process the frame
  if (USBSerial) {  // Use the boolean operator to check if USB is connected
    // Send frame size first
    USBSerial.write((uint8_t*)&fb->len, 4);
    
    // Send frame data
    size_t bytesWritten = USBSerial.write(fb->buf, fb->len);
    
    if (DEBUG_OUTPUT) {
      Serial.printf("Frame: %u bytes, sent: %u bytes\n", fb->len, bytesWritten);
    }
  }
  
  // Return the frame buffer to be reused
  esp_camera_fb_return(fb);
  
  // Small delay to prevent overwhelming the USB bus
  delay(10);
}
