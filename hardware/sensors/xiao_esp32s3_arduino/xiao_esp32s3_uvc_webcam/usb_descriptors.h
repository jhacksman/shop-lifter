// USB descriptors for UVC device
#ifndef USB_DESCRIPTORS_H
#define USB_DESCRIPTORS_H

#include <stdint.h>

// USB Device Descriptor
#define USB_VID                  0x303A  // Espressif VID
#define USB_PID                  0x1001  // Example PID for UVC device
#define USB_BCD                  0x0200  // USB 2.0

// UVC Interface Numbers
#define UVC_CONTROL_INTERFACE    0
#define UVC_STREAMING_INTERFACE  1

// UVC Stream Frame Parameters
#define UVC_WIDTH_VGA            640
#define UVC_HEIGHT_VGA           480
#define UVC_WIDTH_QVGA           320
#define UVC_HEIGHT_QVGA          240
#define UVC_FPS                  15
#define UVC_INTERVAL             (10000000/UVC_FPS)  // 100ns units

// UVC Format: MJPEG
#define UVC_FORMAT_MJPEG         0x01
#define UVC_FRAME_MJPEG          0x01

// USB Endpoint Addresses
#define UVC_EP_CONTROL           0x80    // EP 0 IN
#define UVC_EP_VIDEO             0x81    // EP 1 IN

// USB Configuration
#define USB_CONFIG_POWER         0x32    // 100 mA
#define USB_STRING_MANUFACTURER  "Espressif Systems"
#define USB_STRING_PRODUCT       "XIAO ESP32S3 UVC Webcam"
#define USB_STRING_SERIAL        "123456"

// UVC Class-Specific Descriptors
#define UVC_VS_FORMAT_MJPEG_SIZE 11
#define UVC_VS_FRAME_MJPEG_SIZE  30

// UVC Payload Size
#define UVC_PACKET_SIZE          512

// UVC Descriptor Types
#define UVC_CS_INTERFACE         0x24
#define UVC_CS_ENDPOINT          0x25

// UVC Descriptor Subtypes
#define UVC_VC_HEADER            0x01
#define UVC_VC_INPUT_TERMINAL    0x02
#define UVC_VC_OUTPUT_TERMINAL   0x03
#define UVC_VC_PROCESSING_UNIT   0x05
#define UVC_VS_INPUT_HEADER      0x01
#define UVC_VS_FORMAT_MJPEG      0x04
#define UVC_VS_FRAME_MJPEG       0x05
#define UVC_VS_COLOR_FORMAT      0x0D

// UVC Terminal Types
#define UVC_TT_VENDOR_SPECIFIC   0x0100
#define UVC_TT_STREAMING         0x0101
#define UVC_ITT_CAMERA           0x0201
#define UVC_OTT_DISPLAY          0x0301

// External USB descriptor array declaration
extern const uint8_t usb_descriptors[];

#endif // USB_DESCRIPTORS_H
