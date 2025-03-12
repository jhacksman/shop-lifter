/**
 * XIAO ESP32S3 Sense UVC Webcam
 * 
 * A USB Video Class (UVC) webcam implementation for the XIAO ESP32S3 Sense board.
 * Compatible with the default OV2640 camera and standalone OV2640 cameras.
 * 
 * This sketch implements a standard UVC device that can be used with any
 * webcam software without requiring custom drivers.
 * 
 * Board settings:
 * - Board: "XIAO_ESP32S3"
 * - USB Mode: "USB-OTG"
 * - USB CDC On Boot: "Enabled"
 * - Partition Scheme: "Huge APP (3MB No OTA/1MB SPIFFS)"
 * - PSRAM: "QSPI PSRAM"
 */

#include "esp_camera.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "USB.h"
#include "USBCDC.h"
#include "usb_descriptors.h"

// Camera model selection
#define CAMERA_MODEL_XIAO_ESP32S3
#include "camera_pins.h"

// Debug output
#define DEBUG_OUTPUT 1
#define TAG "UVC_WEBCAM"

// Camera configuration
#define FRAME_SIZE FRAMESIZE_VGA  // 640x480
#define JPEG_QUALITY 12           // 0-63 (lower is better quality)

// UVC configuration
#define UVC_BUFFER_SIZE (32 * 1024)  // 32KB buffer for UVC frames
#define UVC_TASK_PRIORITY 5
#define UVC_TASK_STACK_SIZE 4096

// Frame buffer
camera_fb_t *fb = NULL;
uint8_t *uvc_buffer = NULL;
SemaphoreHandle_t frame_semaphore = NULL;
TaskHandle_t uvc_task_handle = NULL;
bool uvc_streaming_enabled = false;

// USB endpoints
#define EP_CTRL 0
#define EP_IN   1

// UVC control requests
#define UVC_SET_CUR  0x01
#define UVC_GET_CUR  0x81
#define UVC_GET_MIN  0x82
#define UVC_GET_MAX  0x83
#define UVC_GET_RES  0x84
#define UVC_GET_LEN  0x85
#define UVC_GET_INFO 0x86
#define UVC_GET_DEF  0x87

// UVC control selectors
#define VS_PROBE_CONTROL 0x01
#define VS_COMMIT_CONTROL 0x02

// UVC streaming states
typedef enum {
  UVC_STREAM_OFF,
  UVC_STREAM_READY,
  UVC_STREAM_ON
} uvc_stream_state_t;

uvc_stream_state_t uvc_stream_state = UVC_STREAM_OFF;

// UVC probe/commit control structure
typedef struct {
  uint16_t bmHint;
  uint8_t bFormatIndex;
  uint8_t bFrameIndex;
  uint32_t dwFrameInterval;
  uint16_t wKeyFrameRate;
  uint16_t wPFrameRate;
  uint16_t wCompQuality;
  uint16_t wCompWindowSize;
  uint16_t wDelay;
  uint32_t dwMaxVideoFrameSize;
  uint32_t dwMaxPayloadTransferSize;
  uint32_t dwClockFrequency;
  uint8_t bmFramingInfo;
  uint8_t bPreferedVersion;
  uint8_t bMinVersion;
  uint8_t bMaxVersion;
} __attribute__((packed)) uvc_probe_commit_t;

uvc_probe_commit_t uvc_control;

// Forward declarations
void uvc_task(void *pvParameters);
bool handle_uvc_control_request(uint8_t bmRequestType, uint8_t bRequest, uint8_t wValueH, uint8_t wValueL, uint16_t wIndex, uint16_t wLength);
void send_uvc_header(uint8_t *buffer, size_t length, bool end_of_frame);
void init_uvc_control();

void setup() {
  // Initialize serial port
  Serial.begin(115200);
  while(!Serial && millis() < 3000);
  
  Serial.println("XIAO ESP32S3 UVC Webcam");
  
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
  
  // Allocate UVC buffer in PSRAM if available
  if (psramFound()) {
    uvc_buffer = (uint8_t *)heap_caps_malloc(UVC_BUFFER_SIZE, MALLOC_CAP_SPIRAM);
  } else {
    uvc_buffer = (uint8_t *)malloc(UVC_BUFFER_SIZE);
  }
  
  if (!uvc_buffer) {
    Serial.println("Failed to allocate UVC buffer");
    return;
  }
  
  // Create semaphore for frame synchronization
  frame_semaphore = xSemaphoreCreateBinary();
  if (!frame_semaphore) {
    Serial.println("Failed to create frame semaphore");
    return;
  }
  
  // Initialize UVC control structure
  init_uvc_control();
  
  // Initialize USB with custom descriptors
  USB.onControl(handle_uvc_control_request);
  USB.begin();
  
  // Create UVC streaming task
  xTaskCreatePinnedToCore(
    uvc_task,
    "UVC Task",
    UVC_TASK_STACK_SIZE,
    NULL,
    UVC_TASK_PRIORITY,
    &uvc_task_handle,
    1
  );
  
  Serial.println("XIAO ESP32S3 UVC Webcam ready");
}

void loop() {
  // Main loop is empty as UVC streaming is handled by the UVC task
  delay(1000);
  
  if (DEBUG_OUTPUT) {
    // Print memory usage
    Serial.printf("Free heap: %u, Free PSRAM: %u\n", 
      heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
      heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    
    // Print UVC streaming state
    Serial.printf("UVC streaming state: %d\n", uvc_stream_state);
  }
}

// Initialize UVC control structure with default values
void init_uvc_control() {
  memset(&uvc_control, 0, sizeof(uvc_control));
  uvc_control.bmHint = 0x0000;
  uvc_control.bFormatIndex = 1;
  uvc_control.bFrameIndex = 1;
  uvc_control.dwFrameInterval = UVC_INTERVAL;
  uvc_control.wKeyFrameRate = 0;
  uvc_control.wPFrameRate = 0;
  uvc_control.wCompQuality = 0;
  uvc_control.wCompWindowSize = 0;
  uvc_control.wDelay = 0;
  uvc_control.dwMaxVideoFrameSize = UVC_WIDTH_VGA * UVC_HEIGHT_VGA * 2;
  uvc_control.dwMaxPayloadTransferSize = UVC_PACKET_SIZE;
  uvc_control.dwClockFrequency = 0;
  uvc_control.bmFramingInfo = 0;
  uvc_control.bPreferedVersion = 0;
  uvc_control.bMinVersion = 0;
  uvc_control.bMaxVersion = 0;
}

// Handle UVC control requests
bool handle_uvc_control_request(uint8_t bmRequestType, uint8_t bRequest, uint8_t wValueH, uint8_t wValueL, uint16_t wIndex, uint16_t wLength) {
  bool handled = false;
  
  // Check if this is a UVC class-specific request
  if ((bmRequestType & 0x60) == 0x20) {
    uint8_t entity_id = wIndex >> 8;
    uint8_t interface_idx = wIndex & 0xFF;
    
    // Check if this is a video streaming interface request
    if (interface_idx == UVC_STREAMING_INTERFACE) {
      uint8_t control_selector = wValueH;
      
      if (DEBUG_OUTPUT) {
        Serial.printf("UVC control request: 0x%02x, CS: 0x%02x, Len: %d\n", bRequest, control_selector, wLength);
      }
      
      // Handle VS_PROBE_CONTROL and VS_COMMIT_CONTROL
      if (control_selector == VS_PROBE_CONTROL || control_selector == VS_COMMIT_CONTROL) {
        switch (bRequest) {
          case UVC_GET_CUR:
          case UVC_GET_MIN:
          case UVC_GET_MAX:
          case UVC_GET_DEF:
            USB.sendControl((uint8_t*)&uvc_control, sizeof(uvc_control));
            handled = true;
            break;
            
          case UVC_SET_CUR:
            if (wLength == sizeof(uvc_control)) {
              USB.recvControl((uint8_t*)&uvc_control, sizeof(uvc_control));
              
              if (control_selector == VS_COMMIT_CONTROL) {
                // Start or update streaming based on the committed parameters
                if (uvc_stream_state == UVC_STREAM_OFF) {
                  uvc_stream_state = UVC_STREAM_READY;
                }
              }
              
              handled = true;
            }
            break;
        }
      }
    }
  }
  
  return handled;
}

// UVC streaming task
void uvc_task(void *pvParameters) {
  size_t jpeg_size = 0;
  uint32_t frame_count = 0;
  
  while (1) {
    // Check if streaming is enabled
    if (uvc_stream_state == UVC_STREAM_READY) {
      uvc_stream_state = UVC_STREAM_ON;
      if (DEBUG_OUTPUT) {
        Serial.println("UVC streaming started");
      }
    }
    
    if (uvc_stream_state == UVC_STREAM_ON) {
      // Capture frame from camera
      fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("Camera capture failed");
        vTaskDelay(pdMS_TO_TICKS(100));
        continue;
      }
      
      jpeg_size = fb->len;
      
      if (DEBUG_OUTPUT && (frame_count % 30 == 0)) {
        Serial.printf("JPEG: %u bytes, Frame: %u\n", jpeg_size, frame_count);
      }
      
      // Send UVC packets
      if (jpeg_size <= UVC_BUFFER_SIZE) {
        // Copy frame to UVC buffer
        memcpy(uvc_buffer, fb->buf, jpeg_size);
        
        // Send UVC header and payload
        size_t bytes_sent = 0;
        size_t bytes_remaining = jpeg_size;
        uint8_t *data_ptr = uvc_buffer;
        
        while (bytes_remaining > 0) {
          size_t packet_size = bytes_remaining > UVC_PACKET_SIZE ? UVC_PACKET_SIZE : bytes_remaining;
          bool is_last_packet = (bytes_remaining <= UVC_PACKET_SIZE);
          
          // Send UVC header (2 bytes) + payload
          send_uvc_header(data_ptr, packet_size, is_last_packet);
          
          data_ptr += packet_size;
          bytes_sent += packet_size;
          bytes_remaining -= packet_size;
        }
      } else {
        if (DEBUG_OUTPUT) {
          Serial.println("Frame too large for buffer");
        }
      }
      
      // Return the frame buffer to be reused
      esp_camera_fb_return(fb);
      frame_count++;
      
      // Small delay to prevent overwhelming the USB bus
      vTaskDelay(pdMS_TO_TICKS(5));
    } else {
      // Streaming is not active, wait
      vTaskDelay(pdMS_TO_TICKS(100));
    }
  }
}

// Send UVC header and payload
void send_uvc_header(uint8_t *buffer, size_t length, bool end_of_frame) {
  // UVC header (2 bytes)
  uint8_t uvc_header[2] = {0x02, 0x00}; // BFH = 10b (payload data)
  
  if (end_of_frame) {
    uvc_header[1] |= 0x02; // Set EOF bit
  }
  
  // Send header and payload
  USB.sendControl(uvc_header, 2);
  USB.sendControl(buffer, length);
}
