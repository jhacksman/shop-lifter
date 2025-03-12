#include "usb_descriptors.h"

// USB Device Descriptor
static const uint8_t device_descriptor[] = {
  0x12,        // bLength
  0x01,        // bDescriptorType (Device)
  0x00, 0x02,  // bcdUSB 2.00
  0xEF,        // bDeviceClass (Miscellaneous)
  0x02,        // bDeviceSubClass (Common)
  0x01,        // bDeviceProtocol (Interface Association Descriptor)
  0x40,        // bMaxPacketSize0 64
  USB_VID & 0xff, USB_VID >> 8,  // idVendor
  USB_PID & 0xff, USB_PID >> 8,  // idProduct
  0x00, 0x01,  // bcdDevice 1.00
  0x01,        // iManufacturer (String Index)
  0x02,        // iProduct (String Index)
  0x03,        // iSerialNumber (String Index)
  0x01         // bNumConfigurations 1
};

// USB Configuration Descriptor
static const uint8_t config_descriptor[] = {
  // Configuration Descriptor
  0x09,        // bLength
  0x02,        // bDescriptorType (Configuration)
  0xE8, 0x00,  // wTotalLength 232
  0x02,        // bNumInterfaces 2
  0x01,        // bConfigurationValue
  0x00,        // iConfiguration (String Index)
  0x80,        // bmAttributes (Bus Powered)
  USB_CONFIG_POWER,  // bMaxPower 100mA

  // Interface Association Descriptor
  0x08,        // bLength
  0x0B,        // bDescriptorType (Interface Association)
  0x00,        // bFirstInterface
  0x02,        // bInterfaceCount
  0x0E,        // bFunctionClass (Video)
  0x03,        // bFunctionSubClass (Video Interface Collection)
  0x00,        // bFunctionProtocol
  0x00,        // iFunction (String Index)

  // Video Control Interface Descriptor
  0x09,        // bLength
  0x04,        // bDescriptorType (Interface)
  0x00,        // bInterfaceNumber 0
  0x00,        // bAlternateSetting
  0x01,        // bNumEndpoints 1
  0x0E,        // bInterfaceClass (Video)
  0x01,        // bInterfaceSubClass (Video Control)
  0x00,        // bInterfaceProtocol
  0x00,        // iInterface (String Index)

  // Video Control Interface Header Descriptor
  0x0D,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x01,        // bDescriptorSubtype (VC_HEADER)
  0x00, 0x01,  // bcdUVC 1.00
  0x4D, 0x00,  // wTotalLength 77
  0x80, 0x8D, 0x5B, 0x00,  // dwClockFrequency 6,000,000
  0x01,        // bInCollection 1
  0x01,        // baInterfaceNr[0] 1

  // Input Terminal Descriptor (Camera)
  0x12,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x02,        // bDescriptorSubtype (VC_INPUT_TERMINAL)
  0x01,        // bTerminalID
  0x01, 0x02,  // wTerminalType (Camera)
  0x00,        // bAssocTerminal
  0x00,        // iTerminal (String Index)
  0x00, 0x00,  // wObjectiveFocalLengthMin
  0x00, 0x00,  // wObjectiveFocalLengthMax
  0x00, 0x00,  // wOcularFocalLength
  0x03,        // bControlSize
  0x00, 0x00, 0x00, // bmControls

  // Processing Unit Descriptor
  0x0D,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x05,        // bDescriptorSubtype (VC_PROCESSING_UNIT)
  0x02,        // bUnitID
  0x01,        // bSourceID
  0x00, 0x40,  // wMaxMultiplier
  0x03,        // bControlSize
  0x00, 0x00, 0x00, // bmControls
  0x00,        // iProcessing (String Index)
  0x00,        // bmVideoStandards

  // Output Terminal Descriptor
  0x09,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x03,        // bDescriptorSubtype (VC_OUTPUT_TERMINAL)
  0x03,        // bTerminalID
  0x01, 0x01,  // wTerminalType (USB Streaming)
  0x00,        // bAssocTerminal
  0x02,        // bSourceID
  0x00,        // iTerminal (String Index)

  // Video Streaming Interface Descriptor (Alternate Setting 0)
  0x09,        // bLength
  0x04,        // bDescriptorType (Interface)
  0x01,        // bInterfaceNumber 1
  0x00,        // bAlternateSetting
  0x00,        // bNumEndpoints 0
  0x0E,        // bInterfaceClass (Video)
  0x02,        // bInterfaceSubClass (Video Streaming)
  0x00,        // bInterfaceProtocol
  0x00,        // iInterface (String Index)

  // Video Streaming Interface Descriptor (Alternate Setting 1)
  0x09,        // bLength
  0x04,        // bDescriptorType (Interface)
  0x01,        // bInterfaceNumber 1
  0x01,        // bAlternateSetting
  0x01,        // bNumEndpoints 1
  0x0E,        // bInterfaceClass (Video)
  0x02,        // bInterfaceSubClass (Video Streaming)
  0x00,        // bInterfaceProtocol
  0x00,        // iInterface (String Index)

  // Video Streaming Input Header Descriptor
  0x0E,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x01,        // bDescriptorSubtype (VS_INPUT_HEADER)
  0x01,        // bNumFormats 1
  0x4B, 0x00,  // wTotalLength 75
  UVC_EP_VIDEO, // bEndpointAddress (EP 1 IN)
  0x00,        // bmInfo
  0x03,        // bTerminalLink
  0x01,        // bStillCaptureMethod
  0x00,        // bTriggerSupport
  0x00,        // bTriggerUsage
  0x01,        // bControlSize
  0x00,        // bmaControls[0]

  // Video Format Descriptor (MJPEG)
  0x0B,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x06,        // bDescriptorSubtype (VS_FORMAT_MJPEG)
  0x01,        // bFormatIndex 1
  0x01,        // bNumFrameDescriptors 1
  0x01,        // bmFlags (Fixed frame rate)
  0x01,        // bDefaultFrameIndex 1
  0x00,        // bAspectRatioX
  0x00,        // bAspectRatioY
  0x00,        // bmInterlaceFlags
  0x00,        // bCopyProtect

  // Video Frame Descriptor (640x480 @ 15fps)
  0x1E,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x07,        // bDescriptorSubtype (VS_FRAME_MJPEG)
  0x01,        // bFrameIndex 1
  0x01,        // bmCapabilities (Still image supported)
  UVC_WIDTH_VGA & 0xff, UVC_WIDTH_VGA >> 8,    // wWidth 640
  UVC_HEIGHT_VGA & 0xff, UVC_HEIGHT_VGA >> 8,  // wHeight 480
  0x00, 0x00, 0x94, 0x11,  // dwMinBitRate 1,170,432 (15fps * 640 * 480 * 1.5bpp)
  0x00, 0x00, 0x94, 0x11,  // dwMaxBitRate 1,170,432
  0x00, 0x48, 0x3F, 0x00,  // dwMaxVideoFrameBufferSize 4,147,200 (640 * 480 * 3 * 4.5)
  UVC_INTERVAL & 0xff, (UVC_INTERVAL >> 8) & 0xff, (UVC_INTERVAL >> 16) & 0xff, (UVC_INTERVAL >> 24) & 0xff,  // dwDefaultFrameInterval 666,666 (15fps)
  0x01,        // bFrameIntervalType 1 (Discrete)
  UVC_INTERVAL & 0xff, (UVC_INTERVAL >> 8) & 0xff, (UVC_INTERVAL >> 16) & 0xff, (UVC_INTERVAL >> 24) & 0xff,  // dwFrameInterval[0] 666,666 (15fps)

  // Video Frame Descriptor (320x240 @ 30fps)
  0x1E,        // bLength
  0x24,        // bDescriptorType (CS_INTERFACE)
  0x07,        // bDescriptorSubtype (VS_FRAME_MJPEG)
  0x02,        // bFrameIndex 2
  0x01,        // bmCapabilities (Still image supported)
  UVC_WIDTH_QVGA & 0xff, UVC_WIDTH_QVGA >> 8,    // wWidth 320
  UVC_HEIGHT_QVGA & 0xff, UVC_HEIGHT_QVGA >> 8,  // wHeight 240
  0x00, 0x00, 0x25, 0x08,  // dwMinBitRate 530,432 (30fps * 320 * 240 * 1.5bpp)
  0x00, 0x00, 0x25, 0x08,  // dwMaxBitRate 530,432
  0x00, 0x20, 0x1C, 0x00,  // dwMaxVideoFrameBufferSize 1,843,200 (320 * 240 * 3 * 8)
  0x40, 0x42, 0x0F, 0x00,  // dwDefaultFrameInterval 333,333 (30fps)
  0x01,        // bFrameIntervalType 1 (Discrete)
  0x40, 0x42, 0x0F, 0x00,  // dwFrameInterval[0] 333,333 (30fps)

  // Endpoint Descriptor (Video)
  0x07,        // bLength
  0x05,        // bDescriptorType (Endpoint)
  UVC_EP_VIDEO, // bEndpointAddress (EP 1 IN)
  0x02,        // bmAttributes (Bulk)
  UVC_PACKET_SIZE & 0xff, UVC_PACKET_SIZE >> 8,  // wMaxPacketSize 512
  0x00         // bInterval 0
};

// String Descriptors
static const uint8_t string0_descriptor[] = {
  0x04,        // bLength
  0x03,        // bDescriptorType (String)
  0x09, 0x04   // wLANGID[0] (English - United States)
};

static const uint8_t string1_descriptor[] = {
  0x22,        // bLength
  0x03,        // bDescriptorType (String)
  'E', 0, 's', 0, 'p', 0, 'r', 0, 'e', 0, 's', 0, 's', 0, 'i', 0, 'f', 0, ' ', 0, 'S', 0, 'y', 0, 's', 0, 't', 0, 'e', 0, 'm', 0, 's', 0
};

static const uint8_t string2_descriptor[] = {
  0x2C,        // bLength
  0x03,        // bDescriptorType (String)
  'X', 0, 'I', 0, 'A', 0, 'O', 0, ' ', 0, 'E', 0, 'S', 0, 'P', 0, '3', 0, '2', 0, 'S', 0, '3', 0, ' ', 0, 'U', 0, 'V', 0, 'C', 0, ' ', 0, 'W', 0, 'e', 0, 'b', 0, 'c', 0, 'a', 0, 'm', 0
};

static const uint8_t string3_descriptor[] = {
  0x0E,        // bLength
  0x03,        // bDescriptorType (String)
  '1', 0, '2', 0, '3', 0, '4', 0, '5', 0, '6', 0
};

// USB Descriptors array
const uint8_t* const usb_descriptors[] = {
  device_descriptor,
  config_descriptor,
  string0_descriptor,
  string1_descriptor,
  string2_descriptor,
  string3_descriptor,
  NULL  // End of array marker
};

// Export the USB descriptors array
const uint8_t* const* get_usb_descriptors() {
  return usb_descriptors;
}
